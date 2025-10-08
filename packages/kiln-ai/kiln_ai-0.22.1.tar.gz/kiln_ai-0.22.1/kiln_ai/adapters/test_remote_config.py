import asyncio
import json
import logging
import os
from unittest.mock import patch

import pytest

from kiln_ai.adapters.ml_embedding_model_list import (
    EmbeddingModelName,
    KilnEmbeddingModel,
    KilnEmbeddingModelFamily,
    KilnEmbeddingModelProvider,
    built_in_embedding_models,
)
from kiln_ai.adapters.ml_model_list import (
    KilnModel,
    KilnModelProvider,
    ModelFamily,
    ModelName,
    built_in_models,
)
from kiln_ai.adapters.remote_config import (
    KilnRemoteConfig,
    deserialize_config_at_path,
    dump_builtin_config,
    load_from_url,
    load_remote_models,
    serialize_config,
)
from kiln_ai.datamodel.datamodel_enums import (
    KilnMimeType,
    ModelProviderName,
    StructuredOutputMode,
)


@pytest.fixture
def mock_model() -> KilnModel:
    return KilnModel(
        family=ModelFamily.gpt,
        name=ModelName.gpt_4_1,
        friendly_name="GPT 4.1",
        providers=[
            KilnModelProvider(
                name=ModelProviderName.openai,
                model_id="gpt-4.1",
                provider_finetune_id="gpt-4.1-2025-04-14",
                structured_output_mode=StructuredOutputMode.json_schema,
                supports_logprobs=True,
                suggested_for_evals=True,
            ),
            KilnModelProvider(
                name=ModelProviderName.openrouter,
                model_id="openai/gpt-4.1",
                structured_output_mode=StructuredOutputMode.json_schema,
                supports_logprobs=True,
                suggested_for_evals=True,
            ),
            KilnModelProvider(
                name=ModelProviderName.azure_openai,
                model_id="gpt-4.1",
                suggested_for_evals=True,
            ),
        ],
    )


@pytest.fixture
def mock_embedding_model() -> KilnEmbeddingModel:
    return KilnEmbeddingModel(
        family=KilnEmbeddingModelFamily.openai,
        name=EmbeddingModelName.openai_text_embedding_3_small,
        friendly_name="text-embedding-3-small",
        providers=[
            KilnEmbeddingModelProvider(
                name=ModelProviderName.openai,
                model_id="text-embedding-3-small",
                n_dimensions=1536,
                max_input_tokens=8192,
                supports_custom_dimensions=True,
            ),
        ],
    )


def test_round_trip(tmp_path):
    path = tmp_path / "models.json"
    serialize_config(built_in_models, built_in_embedding_models, path)
    loaded = deserialize_config_at_path(path)
    assert [m.model_dump(mode="json") for m in loaded.model_list] == [
        m.model_dump(mode="json") for m in built_in_models
    ]
    assert [m.model_dump(mode="json") for m in loaded.embedding_model_list] == [
        m.model_dump(mode="json") for m in built_in_embedding_models
    ]


def test_load_from_url(mock_model, mock_embedding_model):
    sample_model = mock_model
    sample = [sample_model.model_dump(mode="json")]
    sample_embedding_model = mock_embedding_model
    sample_embedding = [sample_embedding_model.model_dump(mode="json")]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"model_list": sample, "embedding_model_list": sample_embedding}

    with patch(
        "kiln_ai.adapters.remote_config.requests.get", return_value=FakeResponse()
    ):
        remote_config = load_from_url("http://example.com/models.json")

    assert len(remote_config.model_list) == 1
    assert sample_model == remote_config.model_list[0]

    assert len(remote_config.embedding_model_list) == 1
    assert sample_embedding_model == remote_config.embedding_model_list[0]


def test_load_from_url_calls_deserialize_config_data(mock_model, mock_embedding_model):
    """Test that load_from_url calls deserialize_config_data with the model_list from the response."""
    sample_model_data = [mock_model.model_dump(mode="json")]
    sample_embedding_model_data = [mock_embedding_model.model_dump(mode="json")]
    response_data = {
        "model_list": sample_model_data,
        "embedding_model_list": sample_embedding_model_data,
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return response_data

    with (
        patch(
            "kiln_ai.adapters.remote_config.requests.get", return_value=FakeResponse()
        ) as mock_get,
        patch(
            "kiln_ai.adapters.remote_config.deserialize_config_data"
        ) as mock_deserialize,
    ):
        mock_deserialize.return_value = KilnRemoteConfig(
            model_list=[mock_model],
            embedding_model_list=[mock_embedding_model],
        )

        result = load_from_url("http://example.com/models.json")

        # Verify requests.get was called with correct URL
        mock_get.assert_called_once_with("http://example.com/models.json", timeout=10)

        # Verify deserialize_config_data was called with the model_list data
        mock_deserialize.assert_called_once_with(response_data)

        # Verify the result is what deserialize_config_data returned
        assert result.model_list == [mock_model]
        assert result.embedding_model_list == [mock_embedding_model]


def test_dump_builtin_config(tmp_path):
    path = tmp_path / "out.json"
    dump_builtin_config(path)
    loaded = deserialize_config_at_path(path)
    assert [m.model_dump(mode="json") for m in loaded.model_list] == [
        m.model_dump(mode="json") for m in built_in_models
    ]
    assert [m.model_dump(mode="json") for m in loaded.embedding_model_list] == [
        m.model_dump(mode="json") for m in built_in_embedding_models
    ]


async def test_load_remote_models_success(
    monkeypatch, mock_model, mock_embedding_model
):
    del os.environ["KILN_SKIP_REMOTE_MODEL_LIST"]
    sample_models = [mock_model]
    sample_embedding_models = [mock_embedding_model]

    # Save original state to restore later
    original_models = built_in_models.copy()
    original_embedding = built_in_embedding_models.copy()

    try:
        # Mock the load_from_url function to return our test data
        def mock_load_from_url(url):
            return KilnRemoteConfig(
                model_list=sample_models,
                embedding_model_list=sample_embedding_models,
            )

        # Mock the function call
        with patch(
            "kiln_ai.adapters.remote_config.load_from_url",
            side_effect=mock_load_from_url,
        ):
            # Call the function
            load_remote_models("http://example.com/models.json")

            # Wait for the thread to complete
            await asyncio.sleep(0.1)

            # Verify the global state was modified as expected
            assert built_in_models == sample_models
            assert built_in_embedding_models == sample_embedding_models
    finally:
        # Restore original state to prevent test pollution
        built_in_models[:] = original_models
        built_in_embedding_models[:] = original_embedding


@pytest.mark.asyncio
async def test_load_remote_models_failure(monkeypatch):
    # Ensure the environment variable is not set to skip remote model loading
    monkeypatch.delenv("KILN_SKIP_REMOTE_MODEL_LIST", raising=False)

    original_models = built_in_models.copy()
    original_embedding = built_in_embedding_models.copy()

    def fake_fetch(url):
        raise RuntimeError("fail")

    monkeypatch.setattr("kiln_ai.adapters.remote_config.requests.get", fake_fetch)

    with patch("kiln_ai.adapters.remote_config.logger") as mock_logger:
        load_remote_models("http://example.com/models.json")
        assert built_in_models == original_models
        assert built_in_embedding_models == original_embedding

        # assert that logger.warning was called
        mock_logger.warning.assert_called_once()


def test_deserialize_config_with_extra_keys(tmp_path, mock_model):
    # Take a valid model and add an extra key, ensure it is ignored and still loads
    model_dict = mock_model.model_dump(mode="json")
    model_dict["extra_key"] = "should be ignored or error"
    model_dict["providers"][0]["extra_key"] = "should be ignored or error"

    embedding_model_dict = built_in_embedding_models[0].model_dump(mode="json")
    embedding_model_dict["extra_key"] = "should be ignored or error"
    embedding_model_dict["providers"][0]["extra_key"] = "should be ignored or error"

    data = {"model_list": [model_dict], "embedding_model_list": [embedding_model_dict]}
    path = tmp_path / "extra.json"
    path.write_text(json.dumps(data))
    # Should NOT raise, and extra key should be ignored
    models = deserialize_config_at_path(path)
    assert hasattr(models.model_list[0], "family")
    assert not hasattr(models.model_list[0], "extra_key")
    assert hasattr(models.model_list[0], "providers")
    assert not hasattr(models.model_list[0].providers[0], "extra_key")
    assert hasattr(models.embedding_model_list[0], "family")
    assert not hasattr(models.embedding_model_list[0], "extra_key")
    assert hasattr(models.embedding_model_list[0], "providers")
    assert not hasattr(models.embedding_model_list[0].providers[0], "extra_key")


def test_multimodal_fields_specified(tmp_path):
    model_dict = KilnModel(
        family=ModelFamily.gpt,
        name=ModelName.gpt_4o,
        friendly_name="GPT-mock",
        providers=[
            KilnModelProvider(
                name=ModelProviderName.openai,
                model_id="gpt-4o",
                structured_output_mode=StructuredOutputMode.json_schema,
                supports_doc_extraction=True,
                multimodal_capable=True,
                multimodal_mime_types=[
                    KilnMimeType.JPEG,
                    KilnMimeType.PNG,
                ],
            ),
        ],
    ).model_dump(mode="json")

    data = {"model_list": [model_dict], "embedding_model_list": []}
    path = tmp_path / "extra.json"
    path.write_text(json.dumps(data))
    models = deserialize_config_at_path(path)
    assert models.model_list[0].providers[0].supports_doc_extraction
    assert models.model_list[0].providers[0].multimodal_capable
    assert models.model_list[0].providers[0].multimodal_mime_types == [
        KilnMimeType.JPEG,
        KilnMimeType.PNG,
    ]


def test_multimodal_fields_mime_type_forward_compat(tmp_path):
    # This may happen if the current client is out of date with the remote config
    # and we add a new mime type that the old client gets over the air
    model_dict = KilnModel(
        family=ModelFamily.gpt,
        name=ModelName.gpt_4o,
        friendly_name="GPT-mock",
        providers=[
            KilnModelProvider(
                name=ModelProviderName.openai,
                model_id="gpt-4o",
                structured_output_mode=StructuredOutputMode.json_schema,
                supports_doc_extraction=True,
                multimodal_capable=True,
                multimodal_mime_types=[
                    KilnMimeType.JPEG,
                    KilnMimeType.PNG,
                    "new/unknown-mime-type",
                ],
            ),
        ],
    ).model_dump(mode="json")

    data = {"model_list": [model_dict], "embedding_model_list": []}
    path = tmp_path / "extra.json"
    path.write_text(json.dumps(data))
    models = deserialize_config_at_path(path)
    assert models.model_list[0].providers[0].supports_doc_extraction
    assert models.model_list[0].providers[0].multimodal_capable
    multimodal_mime_types = models.model_list[0].providers[0].multimodal_mime_types
    assert multimodal_mime_types is not None
    assert "new/unknown-mime-type" not in multimodal_mime_types
    assert multimodal_mime_types == [
        KilnMimeType.JPEG,
        KilnMimeType.PNG,
    ]


def test_multimodal_fields_not_specified(tmp_path):
    model_dict = KilnModel(
        family=ModelFamily.gpt,
        name=ModelName.gpt_4o,
        friendly_name="GPT-mock",
        providers=[
            KilnModelProvider(
                name=ModelProviderName.openai,
                model_id="gpt-4o",
                structured_output_mode=StructuredOutputMode.json_schema,
            ),
        ],
    ).model_dump(mode="json")

    embedding_model_dict = KilnEmbeddingModel(
        family=KilnEmbeddingModelFamily.openai,
        name=EmbeddingModelName.openai_text_embedding_3_small,
        friendly_name="text-embedding-3-small",
        providers=[
            KilnEmbeddingModelProvider(
                name=ModelProviderName.openai,
                model_id="text-embedding-3-small",
                n_dimensions=1536,
                max_input_tokens=8192,
                supports_custom_dimensions=True,
            ),
        ],
    ).model_dump(mode="json")

    data = {"model_list": [model_dict], "embedding_model_list": [embedding_model_dict]}
    path = tmp_path / "extra.json"
    path.write_text(json.dumps(data))
    remote_config = deserialize_config_at_path(path)

    models = remote_config.model_list
    assert not models[0].providers[0].supports_doc_extraction
    assert not models[0].providers[0].multimodal_capable
    assert models[0].providers[0].multimodal_mime_types is None

    embedding_models = remote_config.embedding_model_list
    assert len(embedding_models) == 1
    assert embedding_models[0].family == KilnEmbeddingModelFamily.openai
    assert embedding_models[0].name == EmbeddingModelName.openai_text_embedding_3_small
    assert embedding_models[0].friendly_name == "text-embedding-3-small"
    assert len(embedding_models[0].providers) == 1
    assert embedding_models[0].providers[0].name == ModelProviderName.openai
    assert embedding_models[0].providers[0].model_id == "text-embedding-3-small"
    assert embedding_models[0].providers[0].n_dimensions == 1536
    assert embedding_models[0].providers[0].max_input_tokens == 8192
    assert embedding_models[0].providers[0].supports_custom_dimensions


def test_deserialize_config_with_invalid_models(tmp_path, caplog, mock_model):
    """Test comprehensive handling of invalid models and providers during deserialization."""

    # Create a fully valid model as baseline
    valid_model = mock_model.model_dump(mode="json")

    # Case 1: Invalid model - missing required field 'family'
    invalid_model_missing_family = mock_model.model_dump(mode="json")
    del invalid_model_missing_family["family"]

    # Case 2: Invalid model - invalid data type for required field
    invalid_model_wrong_type = mock_model.model_dump(mode="json")
    invalid_model_wrong_type["name"] = None  # name should be a string, not None

    # Case 3: Invalid model - completely malformed
    invalid_model_malformed = {"not_a_valid_model": "at_all"}

    # Case 4: Valid model with one invalid provider (should keep model, skip invalid provider)
    valid_model_invalid_provider = mock_model.model_dump(mode="json")
    valid_model_invalid_provider["name"] = "test_model_invalid_provider"  # Unique name
    valid_model_invalid_provider["providers"][0]["name"] = "unknown-provider-123"

    # Case 5: Valid model with mixed valid/invalid providers (should keep model and valid providers)
    valid_model_mixed_providers = mock_model.model_dump(mode="json")
    valid_model_mixed_providers["name"] = "test_model_mixed_providers"  # Unique name
    # Add a second provider that's valid
    valid_provider = valid_model_mixed_providers["providers"][0].copy()
    valid_provider["name"] = "azure_openai"
    # Make first provider invalid
    valid_model_mixed_providers["providers"][0]["name"] = "invalid-provider-1"
    # Add invalid provider with missing required field
    invalid_provider = valid_model_mixed_providers["providers"][0].copy()
    del invalid_provider["name"]
    # Add another invalid provider with wrong type
    invalid_provider_2 = valid_model_mixed_providers["providers"][0].copy()
    invalid_provider_2["supports_structured_output"] = "not_a_boolean"

    valid_model_mixed_providers["providers"] = [
        valid_model_mixed_providers["providers"][0],  # invalid name
        valid_provider,  # valid
        invalid_provider,  # missing name
        invalid_provider_2,  # wrong type
    ]

    # Case 6: Valid model with all invalid providers (should keep model with empty providers)
    valid_model_all_invalid_providers = mock_model.model_dump(mode="json")
    valid_model_all_invalid_providers["name"] = (
        "test_model_all_invalid_providers"  # Unique name
    )
    valid_model_all_invalid_providers["providers"][0]["name"] = "unknown-provider-456"
    if len(valid_model_all_invalid_providers["providers"]) > 1:
        valid_model_all_invalid_providers["providers"][1]["name"] = (
            "another-unknown-provider"
        )
    if len(valid_model_all_invalid_providers["providers"]) > 2:
        valid_model_all_invalid_providers["providers"][2]["name"] = (
            "yet-another-unknown-provider"
        )

    data = {
        "model_list": [
            valid_model,  # Should be kept
            invalid_model_missing_family,  # Should be skipped
            invalid_model_wrong_type,  # Should be skipped
            invalid_model_malformed,  # Should be skipped
            valid_model_invalid_provider,  # Should be kept with empty providers
            valid_model_mixed_providers,  # Should be kept with 1 valid provider
            valid_model_all_invalid_providers,  # Should be kept with empty providers
        ]
    }
    path = tmp_path / "mixed_models.json"
    path.write_text(json.dumps(data))

    # Enable logging to capture warnings
    with caplog.at_level(logging.WARNING):
        remote_config = deserialize_config_at_path(path)

    models = remote_config.model_list

    # Should have 4 valid models (original + 3 with provider issues but valid model structure)
    assert len(models) == 4

    # Check the first model is fully intact
    assert models[0].name == mock_model.name
    assert models[0].family == mock_model.family
    assert len(models[0].providers) == 3  # mock_model has 3 providers

    # Check model with invalid provider has remaining valid providers
    model_with_invalid_provider = next(
        m for m in models if m.name == valid_model_invalid_provider["name"]
    )
    # Should keep the valid providers from the original model (openrouter, azure_openai)
    assert len(model_with_invalid_provider.providers) == 2
    provider_names = {p.name.value for p in model_with_invalid_provider.providers}
    assert provider_names == {"openrouter", "azure_openai"}

    # Check model with mixed providers has only the valid one
    model_with_mixed_providers = next(
        m for m in models if m.name == valid_model_mixed_providers["name"]
    )
    assert len(model_with_mixed_providers.providers) == 1
    assert model_with_mixed_providers.providers[0].name.value == "azure_openai"

    # Check model with all invalid providers has empty providers
    model_with_all_invalid_providers = next(
        m for m in models if m.name == valid_model_all_invalid_providers["name"]
    )
    assert len(model_with_all_invalid_providers.providers) == 0

    # Check warning logs
    warning_logs = [
        record for record in caplog.records if record.levelno == logging.WARNING
    ]

    # Should have warnings for:
    # - 3 invalid models (missing family, wrong type, malformed)
    # - 1 invalid provider in case 4 (unknown-provider-123)
    # - 3 invalid providers in case 5 (invalid-provider-1, missing name, wrong type boolean)
    # - 3 invalid providers in case 6 (unknown-provider-456, another-unknown-provider, yet-another-unknown-provider)
    assert len(warning_logs) >= 10

    # Check that warning messages contain expected content
    model_warnings = [
        log for log in warning_logs if "Failed to validate a model from" in log.message
    ]
    provider_warnings = [
        log
        for log in warning_logs
        if "Failed to validate a model provider" in log.message
    ]

    assert len(model_warnings) == 3  # 3 completely invalid models
    assert (
        len(provider_warnings) == 7
    )  # Exactly 7 invalid providers across different models


def test_deserialize_config_with_invalid_embedding_models(
    tmp_path, caplog, mock_embedding_model
):
    """Test comprehensive handling of invalid embedding models and providers during deserialization."""

    # Create a fully valid embedding model as baseline
    valid_embedding_model = mock_embedding_model.model_dump(mode="json")

    # Case 1: Invalid embedding model - missing required field 'family'
    invalid_embedding_model_missing_family = mock_embedding_model.model_dump(
        mode="json"
    )
    del invalid_embedding_model_missing_family["family"]

    # Case 2: Invalid embedding model - invalid data type for required field
    invalid_embedding_model_wrong_type = mock_embedding_model.model_dump(mode="json")
    invalid_embedding_model_wrong_type["name"] = (
        None  # name should be a string, not None
    )

    # Case 3: Invalid embedding model - completely malformed
    invalid_embedding_model_malformed = {"not_a_valid_embedding_model": "at_all"}

    # Case 4: Valid embedding model with one invalid provider (should keep model, skip invalid provider)
    valid_embedding_model_invalid_provider = mock_embedding_model.model_dump(
        mode="json"
    )
    valid_embedding_model_invalid_provider["name"] = (
        "test_embedding_model_invalid_provider"  # Unique name
    )
    valid_embedding_model_invalid_provider["providers"][0]["name"] = (
        "unknown-provider-123"
    )

    # Case 5: Valid embedding model with mixed valid/invalid providers (should keep model and valid providers)
    valid_embedding_model_mixed_providers = mock_embedding_model.model_dump(mode="json")
    valid_embedding_model_mixed_providers["name"] = (
        "test_embedding_model_mixed_providers"  # Unique name
    )
    # Add a second provider that's valid
    valid_provider = valid_embedding_model_mixed_providers["providers"][0].copy()
    valid_provider["name"] = "azure_openai"
    # Make first provider invalid
    valid_embedding_model_mixed_providers["providers"][0]["name"] = "invalid-provider-1"
    # Add invalid provider with missing required field
    invalid_provider = valid_embedding_model_mixed_providers["providers"][0].copy()
    del invalid_provider["name"]
    # Add another invalid provider with wrong type
    invalid_provider_2 = valid_embedding_model_mixed_providers["providers"][0].copy()
    # Use a known boolean field on KilnModelProvider with a wrong type to force a validation error
    invalid_provider_2["supports_structured_output"] = "not_a_boolean"

    valid_embedding_model_mixed_providers["providers"] = [
        valid_embedding_model_mixed_providers["providers"][0],  # invalid name
        valid_provider,  # valid
        invalid_provider,  # missing name
        invalid_provider_2,  # wrong type
    ]

    # Case 6: Valid embedding model with all invalid providers (should keep model with empty providers)
    valid_embedding_model_all_invalid_providers = mock_embedding_model.model_dump(
        mode="json"
    )
    valid_embedding_model_all_invalid_providers["name"] = (
        "test_embedding_model_all_invalid_providers"  # Unique name
    )
    valid_embedding_model_all_invalid_providers["providers"][0]["name"] = (
        "unknown-provider-456"
    )

    data = {
        "model_list": [],
        "embedding_model_list": [
            valid_embedding_model,  # Should be kept
            invalid_embedding_model_missing_family,  # Should be skipped
            invalid_embedding_model_wrong_type,  # Should be skipped
            invalid_embedding_model_malformed,  # Should be skipped
            valid_embedding_model_invalid_provider,  # Should be kept with empty providers
            valid_embedding_model_mixed_providers,  # Should be kept with 1 valid provider
            valid_embedding_model_all_invalid_providers,  # Should be kept with empty providers
        ],
    }
    path = tmp_path / "mixed_embedding_models.json"
    path.write_text(json.dumps(data))

    # Enable logging to capture warnings
    with caplog.at_level(logging.WARNING):
        remote_config = deserialize_config_at_path(path)

    embedding_models = remote_config.embedding_model_list

    # Should have 4 valid embedding models (original + 3 with provider issues but valid model structure)
    assert len(embedding_models) == 4

    # Check the first embedding model is fully intact
    assert embedding_models[0].name == mock_embedding_model.name
    assert embedding_models[0].family == mock_embedding_model.family
    assert (
        len(embedding_models[0].providers) == 1
    )  # mock_embedding_model has 1 provider

    # Check embedding model with invalid provider has remaining valid providers
    embedding_model_with_invalid_provider = next(
        m
        for m in embedding_models
        if m.name == valid_embedding_model_invalid_provider["name"]
    )
    # Should have no valid providers since the original only had one and it was invalid
    assert len(embedding_model_with_invalid_provider.providers) == 0

    # Check embedding model with mixed providers has only the valid one
    embedding_model_with_mixed_providers = next(
        m
        for m in embedding_models
        if m.name == valid_embedding_model_mixed_providers["name"]
    )
    assert len(embedding_model_with_mixed_providers.providers) == 1
    assert (
        embedding_model_with_mixed_providers.providers[0].name.value == "azure_openai"
    )

    # Check embedding model with all invalid providers has empty providers
    embedding_model_with_all_invalid_providers = next(
        m
        for m in embedding_models
        if m.name == valid_embedding_model_all_invalid_providers["name"]
    )
    assert len(embedding_model_with_all_invalid_providers.providers) == 0

    # Check warning logs
    warning_logs = [
        record for record in caplog.records if record.levelno == logging.WARNING
    ]

    # Should have warnings for:
    # - 3 invalid embedding models (missing family, wrong type, malformed)
    # - 1 invalid provider in case 4 (unknown-provider-123)
    # - 3 invalid providers in case 5 (invalid-provider-1, missing name, wrong type boolean)
    # - 1 invalid provider in case 6 (unknown-provider-456)
    assert len(warning_logs) >= 8

    # Check that warning messages contain expected content
    model_warnings = [
        log
        for log in warning_logs
        if "Failed to validate an embedding model from" in log.message
    ]
    provider_warnings = [
        log
        for log in warning_logs
        if "Failed to validate an embedding model provider" in log.message
    ]

    assert len(model_warnings) == 3  # 3 completely invalid embedding models
    assert (
        len(provider_warnings) == 5
    )  # Exactly 5 invalid providers across different embedding models


def test_deserialize_config_empty_provider_list(
    tmp_path, mock_model, mock_embedding_model
):
    """Test that models with empty provider lists are handled correctly."""
    model_with_empty_providers = mock_model.model_dump(mode="json")
    model_with_empty_providers["providers"] = []
    embedding_model_with_empty_providers = mock_embedding_model.model_dump(mode="json")
    embedding_model_with_empty_providers["providers"] = []

    data = {
        "model_list": [model_with_empty_providers],
        "embedding_model_list": [embedding_model_with_empty_providers],
    }
    path = tmp_path / "empty_providers.json"
    path.write_text(json.dumps(data))

    remote_config = deserialize_config_at_path(path)
    models = remote_config.model_list
    assert len(models) == 1
    assert len(models[0].providers) == 0

    embedding_models = remote_config.embedding_model_list
    assert len(embedding_models) == 1
    assert len(embedding_models[0].providers) == 0


def test_deserialize_config_missing_provider_field(
    tmp_path, caplog, mock_model, mock_embedding_model
):
    """Test that models missing the providers field are handled correctly."""
    model_without_providers = mock_model.model_dump(mode="json")
    del model_without_providers["providers"]

    embedding_model_without_providers = mock_embedding_model.model_dump(mode="json")
    del embedding_model_without_providers["providers"]

    data = {
        "model_list": [model_without_providers],
        "embedding_model_list": [embedding_model_without_providers],
    }
    path = tmp_path / "no_providers.json"
    path.write_text(json.dumps(data))

    with caplog.at_level(logging.WARNING):
        remote_config = deserialize_config_at_path(path)

    models = remote_config.model_list

    embedding_models = remote_config.embedding_model_list

    # Model should be kept with empty providers (deserialize_config handles missing providers gracefully)
    assert len(models) == 1
    assert len(models[0].providers) == 0
    assert models[0].name == mock_model.name

    # Should not have any warnings since the function handles missing providers gracefully
    warning_logs = [
        record for record in caplog.records if record.levelno == logging.WARNING
    ]
    assert len(warning_logs) == 0

    assert len(embedding_models) == 1
    assert len(embedding_models[0].providers) == 0
    assert embedding_models[0].name == mock_embedding_model.name

    # Should not have any warnings since the function handles missing providers gracefully
    warning_logs = [
        record for record in caplog.records if record.levelno == logging.WARNING
    ]
    assert len(warning_logs) == 0


def test_deserialize_config_provider_with_extra_fields(
    tmp_path, mock_model, mock_embedding_model
):
    """Test that providers with extra unknown fields are handled gracefully."""
    model_with_extra_provider_fields = mock_model.model_dump(mode="json")
    model_with_extra_provider_fields["providers"][0]["unknown_field"] = (
        "should_be_ignored"
    )
    model_with_extra_provider_fields["providers"][0]["another_extra"] = {
        "nested": "data"
    }

    embedding_model_with_extra_provider_fields = mock_embedding_model.model_dump(
        mode="json"
    )
    embedding_model_with_extra_provider_fields["providers"][0]["unknown_field"] = (
        "should_be_ignored"
    )
    embedding_model_with_extra_provider_fields["providers"][0]["another_extra"] = {
        "nested": "data"
    }

    data = {
        "model_list": [model_with_extra_provider_fields],
        "embedding_model_list": [embedding_model_with_extra_provider_fields],
    }
    path = tmp_path / "extra_provider_fields.json"
    path.write_text(json.dumps(data))

    remote_config = deserialize_config_at_path(path)
    models = remote_config.model_list
    embedding_models = remote_config.embedding_model_list

    assert len(models) == 1
    assert len(models[0].providers) == 3  # mock_model has 3 providers
    # Extra fields should be ignored, not present in the final object
    assert not hasattr(models[0].providers[0], "unknown_field")
    assert not hasattr(models[0].providers[0], "another_extra")

    assert len(embedding_models) == 1
    assert (
        len(embedding_models[0].providers) == 1
    )  # mock_embedding_model has 1 provider
    # Extra fields should be ignored, not present in the final object
    assert not hasattr(embedding_models[0].providers[0], "unknown_field")
    assert not hasattr(embedding_models[0].providers[0], "another_extra")


def test_deserialize_config_model_with_extra_fields(
    tmp_path, mock_model, mock_embedding_model
):
    """Test that models with extra unknown fields are handled gracefully."""
    model_with_extra_fields = mock_model.model_dump(mode="json")
    model_with_extra_fields["future_field"] = "should_be_ignored"
    model_with_extra_fields["complex_extra"] = {"nested": {"data": [1, 2, 3]}}

    embedding_model_with_extra_fields = mock_embedding_model.model_dump(mode="json")
    embedding_model_with_extra_fields["future_field"] = "should_be_ignored"
    embedding_model_with_extra_fields["complex_extra"] = {"nested": {"data": [1, 2, 3]}}

    data = {
        "model_list": [model_with_extra_fields],
        "embedding_model_list": [embedding_model_with_extra_fields],
    }
    path = tmp_path / "extra_model_fields.json"
    path.write_text(json.dumps(data))

    remote_config = deserialize_config_at_path(path)
    models = remote_config.model_list
    embedding_models = remote_config.embedding_model_list

    assert len(models) == 1
    assert models[0].name == mock_model.name
    # Extra fields should be ignored, not present in the final object
    assert not hasattr(models[0], "future_field")
    assert not hasattr(models[0], "complex_extra")

    assert len(embedding_models) == 1
    assert embedding_models[0].name == mock_embedding_model.name
    # Extra fields should be ignored, not present in the final object
    assert not hasattr(embedding_models[0], "future_field")
    assert not hasattr(embedding_models[0], "complex_extra")


def test_deserialize_config_mixed_valid_invalid_providers_single_model(
    tmp_path, caplog, mock_model, mock_embedding_model
):
    """Test a single model with a mix of valid and invalid providers in detail."""
    model = mock_model.model_dump(mode="json")

    # Create a mix of provider scenarios
    valid_provider_1 = model["providers"][0].copy()
    valid_provider_1["name"] = "openai"

    valid_provider_2 = model["providers"][0].copy()
    valid_provider_2["name"] = "azure_openai"

    invalid_provider_unknown_name = model["providers"][0].copy()
    invalid_provider_unknown_name["name"] = "nonexistent_provider"

    invalid_provider_missing_name = model["providers"][0].copy()
    del invalid_provider_missing_name["name"]

    invalid_provider_wrong_type = model["providers"][0].copy()
    invalid_provider_wrong_type["supports_structured_output"] = "not_a_boolean"

    model["providers"] = [
        valid_provider_1,
        invalid_provider_unknown_name,
        valid_provider_2,
        invalid_provider_missing_name,
        invalid_provider_wrong_type,
    ]

    # Create embedding model with mixed valid/invalid providers
    embedding_model = mock_embedding_model.model_dump(mode="json")

    # Create a mix of embedding provider scenarios
    valid_embedding_provider_1 = embedding_model["providers"][0].copy()
    valid_embedding_provider_1["name"] = "openai"

    valid_embedding_provider_2 = embedding_model["providers"][0].copy()
    valid_embedding_provider_2["name"] = "azure_openai"

    invalid_embedding_provider_unknown_name = embedding_model["providers"][0].copy()
    invalid_embedding_provider_unknown_name["name"] = "nonexistent_embedding_provider"

    invalid_embedding_provider_missing_name = embedding_model["providers"][0].copy()
    del invalid_embedding_provider_missing_name["name"]

    invalid_embedding_provider_wrong_type = embedding_model["providers"][0].copy()
    invalid_embedding_provider_wrong_type["n_dimensions"] = "not_a_number"

    embedding_model["providers"] = [
        valid_embedding_provider_1,
        invalid_embedding_provider_unknown_name,
        valid_embedding_provider_2,
        invalid_embedding_provider_missing_name,
        invalid_embedding_provider_wrong_type,
    ]

    data = {"model_list": [model], "embedding_model_list": [embedding_model]}
    path = tmp_path / "mixed_providers_single.json"
    path.write_text(json.dumps(data))

    with caplog.at_level(logging.WARNING):
        remote_config = deserialize_config_at_path(path)

    models = remote_config.model_list
    embedding_models = remote_config.embedding_model_list

    # Should have 1 model with 2 valid providers
    assert len(models) == 1
    assert len(models[0].providers) == 2
    assert models[0].providers[0].name.value == "openai"
    assert models[0].providers[1].name.value == "azure_openai"

    # Should have 1 embedding model with 2 valid providers
    assert len(embedding_models) == 1
    assert len(embedding_models[0].providers) == 2
    assert embedding_models[0].providers[0].name.value == "openai"
    assert embedding_models[0].providers[1].name.value == "azure_openai"

    # Should have logged 3 model provider validation warnings + 3 embedding model provider validation warnings = 6 total
    model_provider_warnings = [
        log
        for log in caplog.records
        if log.levelno == logging.WARNING
        and "Failed to validate a model provider" in log.message
    ]
    embedding_provider_warnings = [
        log
        for log in caplog.records
        if log.levelno == logging.WARNING
        and "Failed to validate an embedding model provider" in log.message
    ]
    assert len(model_provider_warnings) == 3
    assert len(embedding_provider_warnings) == 3


def test_deserialize_config_empty_json_structures(tmp_path):
    """Test various empty JSON structures."""
    # Test empty model_list
    data = {"model_list": [], "embedding_model_list": []}
    path = tmp_path / "empty_model_list.json"
    path.write_text(json.dumps(data))
    remote_config = deserialize_config_at_path(path)
    models = remote_config.model_list
    embedding_models = remote_config.embedding_model_list

    assert len(models) == 0
    assert len(embedding_models) == 0

    # Test empty object with no model_list key
    path = tmp_path / "empty_object.json"
    path.write_text(json.dumps({}))
    with pytest.raises(ValueError):
        deserialize_config_at_path(path)


def test_backwards_compatibility_with_v0_19(tmp_path):
    """Test that kiln-ai v0.19 (first version with remote config) can parse JSON from current version.

    This ensures our serialization format remains backwards compatible using uv scripts.

    Skipped in CI/CD/VScode (needs UV), so you have to run it from the CLI (fine since it's slow):
    Run from CLI: KILN_TEST_COMPATIBILITY=1 uv run python3 -m pytest libs/core/kiln_ai/adapters/test_remote_config.py::test_backwards_compatibility_with_v0_19 -s -v
    """

    # Skip unless explicitly requested via environment variable
    if not os.environ.get("KILN_TEST_COMPATIBILITY"):
        pytest.skip(
            "Compatibility test skipped. Set KILN_TEST_COMPATIBILITY=1 to run this test."
        )

    import shutil
    import subprocess

    # Check if uv is available
    if not shutil.which("uv"):
        pytest.skip("uv is not available for compatibility test")

    # Create JSON with current version
    current_json_path = tmp_path / "current_models.json"
    serialize_config(built_in_models, built_in_embedding_models, current_json_path)

    # Test script using uv inline script metadata to install v0.19
    test_script = f'''# /// script
# dependencies = [
#   "kiln-ai==0.19.0",
#   "pandas",
# ]
# ///
import sys
import json
from pathlib import Path

# Import from v0.19
try:
    from kiln_ai.adapters.remote_config import deserialize_config_at_path
    from kiln_ai.adapters.ml_model_list import KilnModel

    # Try to deserialize current JSON with v0.19 code
    models = deserialize_config_at_path("{current_json_path}")

    # Basic validation - should have parsed successfully
    assert len(models) > 0
    assert all(isinstance(m, KilnModel) for m in models)

    # Check basic fields exist and have expected types
    for model in models:
        assert hasattr(model, 'family') and isinstance(model.family, str)
        assert hasattr(model, 'name') and isinstance(model.name, str)
        assert hasattr(model, 'friendly_name') and isinstance(model.friendly_name, str)
        assert hasattr(model, 'providers') and isinstance(model.providers, list)

        # Check providers have basic fields
        for provider in model.providers:
            assert hasattr(provider, 'name')

    sys.stdout.write("SUCCESS: v0.19 successfully parsed JSON from current version")
    sys.stdout.write(f"Parsed {{len(models)}} models")

except Exception as e:
    sys.stdout.write(f"ERROR: {{e}}")
    sys.exit(1)
'''

    try:
        # Write the uv script
        script_path = tmp_path / "test_v0_19.py"
        script_path.write_text(test_script)

        # Run the script using uv
        result = subprocess.run(
            ["uv", "run", str(script_path)], capture_output=True, text=True
        )

        # Check if the test passed
        if result.returncode != 0:
            pytest.fail(
                f"v0.19 compatibility test failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            )

        # Verify success message was printed
        assert (
            "SUCCESS: v0.19 successfully parsed JSON from current version"
            in result.stdout
        )

    except subprocess.CalledProcessError as e:
        # If we can't run uv, skip the test (might be network issues, etc.)
        pytest.skip(f"Could not run uv script for compatibility test: {e}")
    except FileNotFoundError:
        # If uv command not found
        pytest.skip("uv command not found for compatibility test")
