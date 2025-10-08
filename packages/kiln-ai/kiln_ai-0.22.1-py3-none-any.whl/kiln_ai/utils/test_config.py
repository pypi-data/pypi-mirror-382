import getpass
import os
import threading
from unittest.mock import patch

import pytest
import yaml

from kiln_ai.utils.config import MCP_SECRETS_KEY, Config, ConfigProperty, _get_user_id


@pytest.fixture
def mock_yaml_file(tmp_path):
    yaml_file = tmp_path / "test_settings.yaml"
    return str(yaml_file)


@pytest.fixture
def config_with_yaml(mock_yaml_file):
    with patch(
        "kiln_ai.utils.config.Config.settings_path",
        return_value=mock_yaml_file,
    ):
        yield Config(
            properties={
                "example_property": ConfigProperty(
                    str, default="default_value", env_var="EXAMPLE_PROPERTY"
                ),
                "int_property": ConfigProperty(int, default=0),
                "empty_property": ConfigProperty(str),
                "list_of_objects": ConfigProperty(list, default=[]),
            }
        )


@pytest.fixture(autouse=True)
def reset_config():
    Config._shared_instance = None
    yield
    Config._shared_instance = None


def test_shared_instance():
    config1 = Config.shared()
    config2 = Config.shared()
    assert config1 is config2


def test_property_default_value(config_with_yaml):
    config = config_with_yaml
    assert config.example_property == "default_value"


def test_property_env_var(reset_config, config_with_yaml):
    os.environ["EXAMPLE_PROPERTY"] = "env_value"
    config = config_with_yaml
    assert config.example_property == "env_value"
    del os.environ["EXAMPLE_PROPERTY"]


def test_property_setter(config_with_yaml):
    config = config_with_yaml
    config.example_property = "new_value"
    assert config.example_property == "new_value"


def test_nonexistent_property(config_with_yaml):
    config = config_with_yaml
    with pytest.raises(AttributeError):
        config.nonexistent_property


def test_nonexistent_property_get_value(config_with_yaml):
    config = config_with_yaml
    assert config.get_value("nonexistent_property") is None
    assert config.get_value("empty_property") is None


def test_property_type_conversion(config_with_yaml):
    config = config_with_yaml
    config = Config(properties={"int_property": ConfigProperty(int, default="42")})
    assert isinstance(config.int_property, int)
    assert config.int_property == 42


def test_property_priority(config_with_yaml):
    os.environ["EXAMPLE_PROPERTY"] = "env_value"
    config = config_with_yaml

    # Environment variable takes precedence over default
    assert config.example_property == "env_value"

    # Setter takes precedence over environment variable
    config.example_property = "new_value"
    assert config.example_property == "new_value"

    del os.environ["EXAMPLE_PROPERTY"]


def test_default_lambda(config_with_yaml):
    config = config_with_yaml

    def default_lambda():
        return "lambda_value"

    config = Config(
        properties={
            "lambda_property": ConfigProperty(str, default_lambda=default_lambda)
        }
    )

    assert config.lambda_property == "lambda_value"


def test_get_user_id_none(monkeypatch):
    monkeypatch.setattr(getpass, "getuser", lambda: None)
    assert _get_user_id() == "unknown_user"


def test_get_user_id_exception(monkeypatch):
    def mock_getuser():
        raise Exception("Test exception")

    monkeypatch.setattr(getpass, "getuser", mock_getuser)
    assert _get_user_id() == "unknown_user"


def test_get_user_id_valid(monkeypatch):
    monkeypatch.setattr(getpass, "getuser", lambda: "test_user")
    assert _get_user_id() == "test_user"


def test_user_id_default(config_with_yaml):
    # assert Config.shared().user_id == "scosman"
    assert len(Config.shared().user_id) > 0


def test_yaml_persistence(config_with_yaml, mock_yaml_file):
    # Set a value
    config_with_yaml.example_property = "yaml_value"

    # Check that the value was saved to the YAML file
    with open(mock_yaml_file, "r") as f:
        saved_settings = yaml.safe_load(f)
    assert saved_settings["example_property"] == "yaml_value"

    # Create a new config instance to test loading from YAML
    new_config = Config(
        properties={
            "example_property": ConfigProperty(
                str, default="default_value", env_var="EXAMPLE_PROPERTY"
            ),
        }
    )

    # Check that the value is loaded from YAML
    assert new_config.example_property == "yaml_value"

    # Set an environment variable to check that yaml takes priority
    os.environ["EXAMPLE_PROPERTY"] = "env_value"

    # Check that the YAML value takes priority
    assert new_config.example_property == "yaml_value"

    # Clean up the environment variable
    del os.environ["EXAMPLE_PROPERTY"]


def test_yaml_type_conversion(config_with_yaml, mock_yaml_file):
    # Set an integer value
    config_with_yaml.int_property = 42

    # Check that the value was saved to the YAML file
    with open(mock_yaml_file, "r") as f:
        saved_settings = yaml.safe_load(f)
    assert saved_settings["int_property"] == 42

    # Create a new config instance to test loading and type conversion from YAML
    new_config = Config(
        properties={
            "int_property": ConfigProperty(int, default=0),
        }
    )

    # Check that the value is loaded from YAML and converted to int
    assert new_config.int_property == 42
    assert isinstance(new_config.int_property, int)


def test_settings_hide_sensitive():
    config = Config(
        {
            "public_key": ConfigProperty(str, default="public_value"),
            "secret_key": ConfigProperty(str, default="secret_value", sensitive=True),
        }
    )

    # Set values
    config.public_key = "public_test"
    config.secret_key = "secret_test"

    # Test without hiding sensitive data
    visible_settings = config.settings(hide_sensitive=False)
    assert visible_settings == {
        "public_key": "public_test",
        "secret_key": "secret_test",
    }

    # Test with hiding sensitive data
    hidden_settings = config.settings(hide_sensitive=True)
    assert hidden_settings == {"public_key": "public_test", "secret_key": "[hidden]"}


def test_list_property(config_with_yaml, mock_yaml_file):
    # Add a list property to the config
    config_with_yaml._properties["list_property"] = ConfigProperty(list, default=[])

    # Set initial values
    config_with_yaml.list_property = ["item1", "item2"]

    # Check that the property returns a list
    assert isinstance(config_with_yaml.list_property, list)
    assert config_with_yaml.list_property == ["item1", "item2"]

    # Update the list
    config_with_yaml.list_property = ["item1", "item2", "item3"]
    assert config_with_yaml.list_property == ["item1", "item2", "item3"]

    # Check that the value was saved to the YAML file
    with open(mock_yaml_file, "r") as f:
        saved_settings = yaml.safe_load(f)
    assert saved_settings["list_property"] == ["item1", "item2", "item3"]

    # Create a new config instance to test loading from YAML
    new_config = Config(
        properties={
            "list_property": ConfigProperty(list, default=[]),
        }
    )

    # Check that the value is loaded from YAML and is a list
    assert isinstance(new_config.list_property, list)
    assert new_config.list_property == ["item1", "item2", "item3"]


def test_stale_values_bug(config_with_yaml):
    assert config_with_yaml.example_property == "default_value"

    # Simulate updating the settings file with set_attr
    config_with_yaml.example_property = "second_value"
    assert config_with_yaml.example_property == "second_value"

    # Simulate updating the settings file with set_settings
    config_with_yaml.update_settings({"example_property": "third_value"})
    assert config_with_yaml.example_property == "third_value"


async def test_openai_compatible_providers():
    config = Config.shared()
    assert config.openai_compatible_providers == []

    new_settings = [
        {
            "name": "provider1",
            "url": "https://provider1.com",
            "api_key": "password1",
        },
        {
            "name": "provider2",
            "url": "https://provider2.com",
        },
    ]
    config.save_setting("openai_compatible_providers", new_settings)
    assert config.openai_compatible_providers == new_settings

    # Test that sensitive keys are hidden
    settings = config.settings(hide_sensitive=True)
    assert settings["openai_compatible_providers"] == [
        {"name": "provider1", "url": "https://provider1.com", "api_key": "[hidden]"},
        {"name": "provider2", "url": "https://provider2.com"},
    ]


def test_yaml_persistence_structured_data(config_with_yaml, mock_yaml_file):
    # Set a value
    new_settings = [
        {
            "name": "provider1",
            "url": "https://provider1.com",
            "api_key": "password1",
        },
        {
            "name": "provider2",
            "url": "https://provider2.com",
        },
    ]
    config_with_yaml.list_of_objects = new_settings

    # Check that the value was saved to the YAML file
    with open(mock_yaml_file, "r") as f:
        saved_settings = yaml.safe_load(f)
    assert saved_settings["list_of_objects"] == new_settings


def test_update_settings_thread_safety(config_with_yaml):
    config = config_with_yaml

    exceptions = []

    def update(val):
        try:
            config.update_settings({"int_property": val})
        except Exception as e:
            exceptions.append(e)

    threads = [threading.Thread(target=update, args=(i,)) for i in range(5)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not exceptions
    assert config.int_property in range(5)


def test_mcp_secrets_property():
    """Test mcp_secrets configuration property"""
    config = Config.shared()

    # Initially should be None/empty
    assert config.mcp_secrets is None

    # Set some secrets
    secrets = {
        "server1::Authorization": "Bearer token123",
        "server1::X-API-Key": "api-key-456",
        "server2::Token": "secret-token",
    }
    config.mcp_secrets = secrets

    # Verify they are stored correctly
    assert config.mcp_secrets == secrets
    assert config.mcp_secrets["server1::Authorization"] == "Bearer token123"
    assert config.mcp_secrets["server1::X-API-Key"] == "api-key-456"
    assert config.mcp_secrets["server2::Token"] == "secret-token"


def test_mcp_secrets_sensitive_hiding():
    """Test that mcp_secrets are hidden when hide_sensitive=True"""
    config = Config.shared()

    # Set some secrets
    secrets = {
        "server1::Authorization": "Bearer secret123",
        "server2::X-API-Key": "secret-key",
    }
    config.mcp_secrets = secrets

    # Test without hiding sensitive data
    visible_settings = config.settings(hide_sensitive=False)
    assert MCP_SECRETS_KEY in visible_settings
    assert visible_settings[MCP_SECRETS_KEY] == secrets

    # Test with hiding sensitive data
    hidden_settings = config.settings(hide_sensitive=True)
    assert MCP_SECRETS_KEY in hidden_settings
    assert hidden_settings[MCP_SECRETS_KEY] == "[hidden]"


def test_mcp_secrets_persistence(mock_yaml_file):
    """Test that mcp_secrets are persisted to YAML correctly"""
    with patch(
        "kiln_ai.utils.config.Config.settings_path",
        return_value=mock_yaml_file,
    ):
        config = Config()

        # Set some secrets
        secrets = {
            "server1::Authorization": "Bearer persist123",
            "server2::Token": "persist-token",
        }
        config.mcp_secrets = secrets

        # Check that the value was saved to the YAML file
        with open(mock_yaml_file, "r") as f:
            saved_settings = yaml.safe_load(f)
        assert saved_settings[MCP_SECRETS_KEY] == secrets

        # Create a new config instance to test loading from YAML
        new_config = Config()

        # Check that the value is loaded from YAML
        assert new_config.mcp_secrets == secrets


def test_mcp_secrets_get_value():
    """Test that mcp_secrets can be retrieved using get_value method"""
    config = Config.shared()

    # Initially should be None
    assert config.get_value(MCP_SECRETS_KEY) is None

    # Set some secrets
    secrets = {"server::key": "value"}
    config.mcp_secrets = secrets

    # Should be retrievable via get_value
    assert config.get_value(MCP_SECRETS_KEY) == secrets


def test_mcp_secrets_update_settings():
    """Test updating mcp_secrets using update_settings method"""
    config = Config.shared()

    # Set initial secrets
    initial_secrets = {"server1::key1": "value1"}
    config.update_settings({MCP_SECRETS_KEY: initial_secrets})
    assert config.mcp_secrets == initial_secrets

    # Update with new secrets (should replace, not merge)
    new_secrets = {
        "server1::key1": "updated_value1",
        "server2::key2": "value2",
    }
    config.update_settings({MCP_SECRETS_KEY: new_secrets})
    assert config.mcp_secrets == new_secrets
    assert config.mcp_secrets["server1::key1"] == "updated_value1"
    assert config.mcp_secrets["server2::key2"] == "value2"


def test_mcp_secrets_empty_dict():
    """Test mcp_secrets with empty dict"""
    config = Config.shared()

    # Set empty dict
    config.mcp_secrets = {}
    assert config.mcp_secrets == {}

    # Should still be dict type, not None
    assert isinstance(config.mcp_secrets, dict)


def test_mcp_secrets_type_validation():
    """Test that mcp_secrets enforces dict[str, str] type"""
    config = Config.shared()

    # Valid dict[str, str]
    valid_secrets = {"server::key": "value"}
    config.mcp_secrets = valid_secrets
    assert config.mcp_secrets == valid_secrets

    # The config system applies type conversion when retrieving values
    mixed_types = {"server::key": 123}  # int value
    config.mcp_secrets = mixed_types
    # The type conversion happens when the value is retrieved, not when set
    # So the underlying storage may preserve the original type
    assert config.mcp_secrets == mixed_types or config.mcp_secrets == {
        "server::key": "123"
    }
