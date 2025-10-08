import datetime
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from kiln_ai.adapters.model_adapters.base_adapter import BaseAdapter
from kiln_ai.adapters.run_output import RunOutput
from kiln_ai.datamodel import Task, TaskRun
from kiln_ai.datamodel.basemodel import (
    KilnBaseModel,
    KilnParentedModel,
    name_validator,
    string_to_valid_name,
)
from kiln_ai.datamodel.model_cache import ModelCache
from kiln_ai.datamodel.task import RunConfigProperties


@pytest.fixture
def test_base_file(tmp_path) -> Path:
    test_file_path = tmp_path / "test_model.json"
    data = {"v": 1, "model_type": "kiln_base_model"}

    with open(test_file_path, "w") as file:
        json.dump(data, file, indent=4)

    return test_file_path


@pytest.fixture
def test_base_parented_file(tmp_path) -> Path:
    test_file_path = tmp_path / "test_model.json"
    data = {"v": 1, "model_type": "base_parent_example"}

    with open(test_file_path, "w") as file:
        json.dump(data, file, indent=4)

    return test_file_path


@pytest.fixture
def test_newer_file(tmp_path) -> Path:
    test_file_path = tmp_path / "test_model_sv.json"
    data = {"v": 99}

    with open(test_file_path, "w") as file:
        json.dump(data, file, indent=4)

    return test_file_path


@pytest.fixture
def tmp_model_cache():
    temp_cache = ModelCache()
    # We're testing integration, not cache functions, in this file
    temp_cache._enabled = True
    with (
        patch("kiln_ai.datamodel.basemodel.ModelCache.shared", return_value=temp_cache),
    ):
        yield temp_cache


def test_load_from_file(test_base_file):
    model = KilnBaseModel.load_from_file(test_base_file)
    assert model.v == 1
    assert model.path == test_base_file


def test_save_to_file(test_base_file):
    model = KilnBaseModel(path=test_base_file)
    model.save_to_file()

    with open(test_base_file, "r") as file:
        data = json.load(file)

    assert data["v"] == 1
    assert data["model_type"] == "kiln_base_model"


def test_save_to_file_without_path():
    model = KilnBaseModel()
    with pytest.raises(ValueError):
        model.save_to_file()


def test_max_schema_version(test_newer_file):
    with pytest.raises(ValueError):
        KilnBaseModel.load_from_file(test_newer_file)


def test_type_name():
    model = KilnBaseModel()
    assert model.model_type == "kiln_base_model"


def test_created_atby():
    model = KilnBaseModel()
    assert model.created_at is not None
    # Check it's within 2 seconds of now
    now = datetime.datetime.now()
    assert abs((model.created_at - now).total_seconds()) < 2

    # Created by
    assert len(model.created_by) > 0
    # assert model.created_by == "scosman"


# Instance of the parented model for abstract methods
class NamedParentedModel(KilnParentedModel):
    @classmethod
    def relationship_name(cls) -> str:
        return "tests"

    @classmethod
    def parent_type(cls):
        return KilnBaseModel


def test_parented_model_path_gen(tmp_path):
    parent = KilnBaseModel(path=tmp_path)
    assert parent.id is not None
    child = NamedParentedModel(parent=parent)
    child_path = child.build_path()
    assert child_path.name == "named_parented_model.kiln"
    assert child_path.parent.name == child.id
    assert child_path.parent.parent.name == "tests"
    assert child_path.parent.parent.parent == tmp_path.parent


class BaseParentExample(KilnBaseModel):
    name: Optional[str] = None


# Instance of the parented model for abstract methods, with default name builder
class DefaultParentedModel(KilnParentedModel):
    name: Optional[str] = None

    @classmethod
    def relationship_name(self):
        return "children"

    @classmethod
    def parent_type(cls):
        return BaseParentExample


def test_build_default_child_filename(tmp_path):
    parent = BaseParentExample(path=tmp_path)
    child = DefaultParentedModel(parent=parent)
    child_path = child.build_path()
    assert child_path.name == "default_parented_model.kiln"
    assert child_path.parent.name == child.id
    assert child_path.parent.parent.name == "children"
    assert child_path.parent.parent.parent == tmp_path.parent
    # now with name
    child = DefaultParentedModel(parent=parent, name="Name")
    child_path = child.build_path()
    assert child_path.name == "default_parented_model.kiln"
    assert child_path.parent.name == child.id + " - Name"
    assert child_path.parent.parent.name == "children"
    assert child_path.parent.parent.parent == tmp_path.parent


def test_serialize_child(tmp_path):
    parent = BaseParentExample(path=tmp_path)
    child = DefaultParentedModel(parent=parent, name="Name")

    expected_path = child.build_path()
    assert child.path is None
    child.save_to_file()

    # ensure we save exact path
    assert child.path is not None
    assert child.path == expected_path

    # should have made the directory, and saved the file
    with open(child.path, "r") as file:
        data = json.load(file)

    assert data["v"] == 1
    assert data["name"] == "Name"
    assert data["model_type"] == "default_parented_model"
    assert len(data["id"]) == 12
    assert child.path.parent.name == child.id + " - Name"
    assert child.path.parent.parent.name == "children"
    assert child.path.parent.parent.parent == tmp_path.parent

    # change name, see it serializes, but path stays the same
    child.name = "Name2"
    child.save_to_file()
    assert child.path == expected_path
    with open(child.path, "r") as file:
        data = json.load(file)
    assert data["name"] == "Name2"


def test_save_to_set_location(tmp_path):
    # Keeps the OG path if parent and path are both set
    parent = BaseParentExample(path=tmp_path)
    child_path = tmp_path.parent / "child.kiln"
    child = DefaultParentedModel(path=child_path, parent=parent, name="Name")
    assert child.build_path() == child_path

    # check file created at child_path, not the default smart path
    assert not child_path.exists()
    child.save_to_file()
    assert child_path.exists()

    # if we don't set the path, use the parent + smartpath
    child2 = DefaultParentedModel(parent=parent, name="Name2")
    assert child2.build_path().parent.name == child2.id + " - Name2"
    assert child2.build_path().parent.parent.name == "children"
    assert child2.build_path().parent.parent.parent == tmp_path.parent


def test_parent_without_path():
    # no path from parent or direct path
    parent = BaseParentExample()
    child = DefaultParentedModel(parent=parent, name="Name")
    with pytest.raises(ValueError):
        child.save_to_file()


def test_parent_wrong_type():
    # DefaultParentedModel is parented to BaseParentExample, not KilnBaseModel
    parent = KilnBaseModel()
    with pytest.raises(ValueError):
        DefaultParentedModel(parent=parent, name="Name")


def test_load_children(test_base_parented_file):
    # Set up parent and children models
    parent = BaseParentExample.load_from_file(test_base_parented_file)

    child1 = DefaultParentedModel(parent=parent, name="Child1")
    child2 = DefaultParentedModel(parent=parent, name="Child2")
    child3 = DefaultParentedModel(parent=parent, name="Child3")

    # Ensure the children are saved correctly
    child1.save_to_file()
    child2.save_to_file()
    child3.save_to_file()

    # Load children from parent path
    children = DefaultParentedModel.all_children_of_parent_path(test_base_parented_file)

    # Verify that all children are loaded correctly
    assert len(children) == 3
    names = [child.name for child in children]
    assert "Child1" in names
    assert "Child2" in names
    assert "Child3" in names
    assert all(child.model_type == "default_parented_model" for child in children)


def test_base_filename():
    model = DefaultParentedModel(name="Test")
    assert model.base_filename() == "default_parented_model.kiln"
    model = NamedParentedModel(name="Test")
    assert model.base_filename() == "named_parented_model.kiln"
    assert NamedParentedModel.base_filename() == "named_parented_model.kiln"


def test_load_from_folder(test_base_parented_file):
    parent = BaseParentExample.load_from_file(test_base_parented_file)
    child1 = DefaultParentedModel(parent=parent, name="Child1")
    child1.save_to_file()

    loaded_child1 = DefaultParentedModel.load_from_folder(child1.path.parent)
    assert loaded_child1.name == "Child1"


def test_lazy_load_parent(tmp_path):
    # Create a parent
    parent = BaseParentExample(
        name="Parent", path=(tmp_path / BaseParentExample.base_filename())
    )
    parent.save_to_file()

    # Create a child
    child = DefaultParentedModel(parent=parent, name="Child")
    child.save_to_file()

    # Load the child by path
    loaded_child = DefaultParentedModel.load_from_file(child.path)

    # Access the parent to trigger lazy loading
    loaded_parent = loaded_child.parent

    # Verify that the parent is now loaded and correct
    assert loaded_parent is not None
    assert loaded_parent.name == "Parent"
    assert loaded_parent.path == parent.path

    # Verify that the parent is cached
    assert loaded_child.cached_parent() is loaded_parent


def test_delete(tmp_path):
    # Test deleting a file
    file_path = tmp_path / "test.kiln"
    model = KilnBaseModel(path=file_path)
    model.save_to_file()
    assert file_path.exists()
    model.delete()
    assert not file_path.exists()
    assert not file_path.parent.exists()
    assert model.path is None


def test_delete_dir(tmp_path):
    # Test deleting a directory
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir(parents=True)
    model = KilnBaseModel(path=dir_path)
    assert dir_path.exists()
    model.delete()
    assert not dir_path.exists()
    assert model.path is None


def test_delete_no_path():
    # Test deleting with no path
    model = KilnBaseModel()
    with pytest.raises(ValueError, match="Cannot delete model because path is not set"):
        model.delete()


@pytest.mark.parametrize(
    "name,expected",
    [
        # Basic valid strings remain unchanged
        ("Hello World", "Hello World"),
        ("Test-123", "Test-123"),
        ("my_file_name", "my_file_name"),
        ("multiple!!!symbols", "multiple!!!symbols"),
        # Emoji
        ("Hello 👍", "Hello 👍"),
        # Invalid characters are replaced
        ("Hello@World!", "Hello@World!"),
        ("File.name.txt", "File name txt"),
        ("Special%%%Chars", "Special Chars"),
        ("Special#$%Chars", "Special#$ Chars"),
        # Consecutive invalid characters are replaced
        ("Special%%%Chars", "Special Chars"),
        ("path/to/file", "path to file"),
        # Leading/trailing special characters are removed
        ("__test__", "test"),
        ("...test...", "test"),
        # Whitespace is replaced
        ("", ""),
        ("   ", ""),
        ("Hello   World", "Hello World"),
        # Unicode characters are replaced
        ("你好", "你好"),
        ("你好_世界", "你好_世界"),
        ("你好_世界_你好", "你好_世界_你好"),
        # Newlines, tabs, and other control characters are replaced
        ("Hello\nworld", "Hello world"),
        ("Hello\tworld", "Hello world"),
        ("Hello\rworld", "Hello world"),
        ("Hello\fworld", "Hello world"),
        ("Hello\bworld", "Hello world"),
        ("Hello\vworld", "Hello world"),
        ("Hello\0world", "Hello world"),
        ("Hello\x00world", "Hello world"),
    ],
)
def test_string_to_valid_name(tmp_path, name, expected):
    assert string_to_valid_name(name) == expected

    # check we can create a folder with the valid name
    dir_path = tmp_path / str(uuid.uuid4()) / expected
    dir_path.mkdir(parents=True)


@pytest.mark.parametrize(
    "name,min_length,max_length,should_pass",
    [
        # Valid cases
        ("ValidName", 5, 20, True),
        ("Short", 1, 10, True),
        ("LongerValidName", 5, 20, True),
        # None case (line 53)
        (None, 5, 20, False),
        # Too short cases (lines 57-59)
        ("Hi", 5, 20, False),
        ("", 1, 20, False),
        ("a", 2, 20, False),
        # Too long cases (lines 61-63)
        ("ThisNameIsTooLong", 5, 10, False),
        ("VeryVeryVeryLongName", 1, 15, False),
    ],
)
def test_name_validator_error_conditions(name, min_length, max_length, should_pass):
    validator = name_validator(min_length=min_length, max_length=max_length)

    if should_pass:
        result = validator(name)
        assert result == name
    else:
        with pytest.raises(ValueError):
            validator(name)


def test_load_from_file_with_cache(test_base_file, tmp_model_cache):
    tmp_model_cache.get_model = MagicMock(return_value=None)
    tmp_model_cache.set_model = MagicMock()

    # Load the model
    model = KilnBaseModel.load_from_file(test_base_file)

    # Check that the cache was checked and set
    tmp_model_cache.get_model.assert_called_once_with(
        test_base_file, KilnBaseModel, readonly=False
    )
    tmp_model_cache.set_model.assert_called_once()

    # Ensure the model is correctly loaded
    assert model.v == 1
    assert model.path == test_base_file


def test_save_to_file_invalidates_cache(test_base_file, tmp_model_cache):
    # Create and save the model
    model = KilnBaseModel(path=test_base_file)

    # Set mock after to ignore any previous calls, we want to see save calls it
    tmp_model_cache.invalidate = MagicMock()
    model.save_to_file()

    # Check that the cache was invalidated. Might be called multiple times for setting props like path. but must be called at least once.
    tmp_model_cache.invalidate.assert_called_with(test_base_file)


def test_delete_invalidates_cache(tmp_path, tmp_model_cache):
    # Create and save the model
    file_path = tmp_path / "test.kiln"
    model = KilnBaseModel(path=file_path)
    model.save_to_file()

    # populate and check cache
    model = KilnBaseModel.load_from_file(file_path)
    cached_model = tmp_model_cache.get_model(file_path, KilnBaseModel)
    assert cached_model.id == model.id

    tmp_model_cache.invalidate = MagicMock()

    # Delete the model
    model.delete()

    # Check that the cache was invalidated
    tmp_model_cache.invalidate.assert_called_with(file_path)
    assert tmp_model_cache.get_model(file_path, KilnBaseModel) is None


def test_load_from_file_with_cached_model(test_base_file, tmp_model_cache):
    # Set up the mock to return a cached model
    cached_model = KilnBaseModel(v=1, path=test_base_file)
    tmp_model_cache.get_model = MagicMock(return_value=cached_model)

    with patch("builtins.open", create=True) as mock_open:
        # Load the model
        model = KilnBaseModel.load_from_file(test_base_file)

        # Check that the cache was checked and the cached model was returned
        tmp_model_cache.get_model.assert_called_once_with(
            test_base_file, KilnBaseModel, readonly=False
        )
        assert model is cached_model

        # Assert that open was not called (we used the cached model, not file)
        mock_open.assert_not_called()


def test_from_id_and_parent_path(test_base_parented_file, tmp_model_cache):
    # Set up parent and children models
    parent = BaseParentExample.load_from_file(test_base_parented_file)

    child1 = DefaultParentedModel(parent=parent, name="Child1")
    child2 = DefaultParentedModel(parent=parent, name="Child2")
    child3 = DefaultParentedModel(parent=parent, name="Child3")

    # Save all children
    child1.save_to_file()
    child2.save_to_file()
    child3.save_to_file()

    # Test finding existing child by ID
    assert child2.id is not None  # Type safety
    found_child = DefaultParentedModel.from_id_and_parent_path(
        child2.id, test_base_parented_file
    )
    assert found_child is not None
    assert found_child.id == child2.id
    assert found_child.name == "Child2"
    assert found_child is not child2  # not same instance (deep copy)

    # Test non-existent ID returns None
    not_found = DefaultParentedModel.from_id_and_parent_path(
        "nonexistent", test_base_parented_file
    )
    assert not_found is None


def test_from_id_and_parent_path_with_cache(test_base_parented_file, tmp_model_cache):
    # Set up parent and child
    parent = BaseParentExample.load_from_file(test_base_parented_file)
    child = DefaultParentedModel(parent=parent, name="Child")
    child.save_to_file()

    # First load to populate cache
    assert child.id is not None  # Type safety
    _ = DefaultParentedModel.from_id_and_parent_path(child.id, test_base_parented_file)

    # Mock cache to verify it's used
    tmp_model_cache.get_model_id = MagicMock(return_value=child.id)

    # Load again - should use cache
    found_child = DefaultParentedModel.from_id_and_parent_path(
        child.id, test_base_parented_file
    )

    assert found_child is not None
    assert found_child.id == child.id
    tmp_model_cache.get_model_id.assert_called()


def test_from_id_and_parent_path_without_parent():
    # Test with None parent_path
    not_found = DefaultParentedModel.from_id_and_parent_path("any-id", None)
    assert not_found is None


def test_from_ids_and_parent_path_basic(test_base_parented_file, tmp_model_cache):
    """Test basic functionality of from_ids_and_parent_path method"""
    # Set up parent and children models
    parent = BaseParentExample.load_from_file(test_base_parented_file)

    child1 = DefaultParentedModel(parent=parent, name="Child1")
    child2 = DefaultParentedModel(parent=parent, name="Child2")
    child3 = DefaultParentedModel(parent=parent, name="Child3")

    # Save all children
    child1.save_to_file()
    child2.save_to_file()
    child3.save_to_file()

    # Test finding multiple children by IDs
    assert child1.id is not None and child2.id is not None  # Type safety
    target_ids = {child1.id, child3.id}
    found_children = DefaultParentedModel.from_ids_and_parent_path(
        target_ids, test_base_parented_file
    )

    # Verify correct children were found
    assert len(found_children) == 2
    assert child1.id in found_children
    assert child3.id in found_children
    assert child2.id not in found_children

    # Verify the returned models have correct data
    assert found_children[child1.id].name == "Child1"
    assert found_children[child3.id].name == "Child3"

    # Verify they are not the same instances (deep copies)
    assert found_children[child1.id] is not child1
    assert found_children[child3.id] is not child3


def test_from_ids_and_parent_path_empty_list(test_base_parented_file):
    """Test from_ids_and_parent_path with empty ID list"""
    found_children = DefaultParentedModel.from_ids_and_parent_path(
        set(), test_base_parented_file
    )
    assert found_children == {}


def test_from_ids_and_parent_path_none_parent():
    """Test from_ids_and_parent_path with None parent_path"""
    found_children = DefaultParentedModel.from_ids_and_parent_path({"any-id"}, None)
    assert found_children == {}


def test_from_ids_and_parent_path_no_matches(test_base_parented_file, tmp_model_cache):
    """Test from_ids_and_parent_path when no IDs match existing children"""
    # Set up parent and children models
    parent = BaseParentExample.load_from_file(test_base_parented_file)

    child1 = DefaultParentedModel(parent=parent, name="Child1")
    child1.save_to_file()

    # Test with non-existent IDs
    found_children = DefaultParentedModel.from_ids_and_parent_path(
        {"nonexistent1", "nonexistent2"}, test_base_parented_file
    )
    assert found_children == {}


def test_from_ids_and_parent_path_partial_matches(
    test_base_parented_file, tmp_model_cache
):
    """Test from_ids_and_parent_path when only some IDs match"""
    # Set up parent and children models
    parent = BaseParentExample.load_from_file(test_base_parented_file)

    child1 = DefaultParentedModel(parent=parent, name="Child1")
    child2 = DefaultParentedModel(parent=parent, name="Child2")

    # Save children
    child1.save_to_file()
    child2.save_to_file()

    # Test with mix of existing and non-existent IDs
    assert child1.id is not None and child2.id is not None  # Type safety
    target_ids = {child1.id, "nonexistent", child2.id, "another_nonexistent"}
    found_children = DefaultParentedModel.from_ids_and_parent_path(
        target_ids, test_base_parented_file
    )

    # Should only find the existing children
    assert len(found_children) == 2
    assert child1.id in found_children
    assert child2.id in found_children
    assert "nonexistent" not in found_children
    assert "another_nonexistent" not in found_children


def test_from_ids_and_parent_path_with_cache_fallback(
    test_base_parented_file, tmp_model_cache
):
    """Test from_ids_and_parent_path when cache returns None and needs to load file"""
    # Set up parent and child
    parent = BaseParentExample.load_from_file(test_base_parented_file)
    child = DefaultParentedModel(parent=parent, name="Child")
    child.save_to_file()

    # Mock cache to return None for get_model_id, forcing file load
    tmp_model_cache.get_model_id = MagicMock(return_value=None)

    # Test should still work by loading the file
    assert child.id is not None  # Type safety
    found_children = DefaultParentedModel.from_ids_and_parent_path(
        {child.id}, test_base_parented_file
    )

    assert len(found_children) == 1
    assert child.id in found_children
    assert found_children[child.id].name == "Child"

    # Verify cache was checked
    tmp_model_cache.get_model_id.assert_called()


def test_from_ids_and_parent_path_equivalent_to_individual_lookups(
    test_base_parented_file, tmp_model_cache
):
    """Test that from_ids_and_parent_path returns the same results as individual lookups"""
    # Set up parent and multiple children
    parent = BaseParentExample.load_from_file(test_base_parented_file)

    children = []
    for i in range(10):
        child = DefaultParentedModel(parent=parent, name=f"Child{i}")
        child.save_to_file()
        children.append(child)

    # Select 5 children to lookup
    target_ids = {
        child.id for child in children[::2] if child.id is not None
    }  # Every other child
    assert len(target_ids) == 5  # Ensure we have 5 children to test

    # Test bulk method
    bulk_results = DefaultParentedModel.from_ids_and_parent_path(
        target_ids, test_base_parented_file
    )

    # Test individual method
    individual_results = {}
    for target_id in target_ids:
        result = DefaultParentedModel.from_id_and_parent_path(
            target_id, test_base_parented_file
        )
        if result:
            individual_results[target_id] = result

    # Results should be equivalent
    assert len(bulk_results) == len(individual_results) == 5

    for target_id in target_ids:
        assert target_id in bulk_results
        assert target_id in individual_results

        # Compare the key attributes
        bulk_child = bulk_results[target_id]
        individual_child = individual_results[target_id]

        assert bulk_child.id == individual_child.id
        assert bulk_child.name == individual_child.name
        assert bulk_child.model_type == individual_child.model_type


# Not actually paid, but we want the "must be run manually" feature of the paid marker as this is very slow
@pytest.mark.paid
@pytest.mark.parametrize("num_children", [100, 1000, 2500, 5000])
def test_from_ids_and_parent_path_benchmark(
    test_base_parented_file, tmp_model_cache, num_children
):
    """Benchmark test for from_ids_and_parent_path method performance at scale"""
    # Set up parent and many children
    parent = BaseParentExample.load_from_file(test_base_parented_file)

    children = []
    for i in range(num_children):
        child = DefaultParentedModel(parent=parent, name=f"Child{i:05d}")
        child.save_to_file()
        children.append(child)

    # look up all children
    lookup_count = num_children
    target_ids = {child.id for child in children[:lookup_count] if child.id is not None}
    assert len(target_ids) == lookup_count

    # Benchmark the bulk method using manual timing
    def bulk_lookup():
        return DefaultParentedModel.from_ids_and_parent_path(
            target_ids, test_base_parented_file
        )

    # Run bulk method once and time it
    start_time = time.perf_counter()
    bulk_result = bulk_lookup()
    end_time = time.perf_counter()
    bulk_time = end_time - start_time

    # Verify we got the expected results
    assert len(bulk_result) == lookup_count

    # Calculate bulk method stats
    bulk_ops_per_second = lookup_count / bulk_time

    # Benchmark the individual lookup method using manual timing
    def individual_lookups():
        results = {}
        for target_id in target_ids:
            result = DefaultParentedModel.from_id_and_parent_path(
                target_id, test_base_parented_file
            )
            if result:
                results[target_id] = result
        return results

    # Run individual lookup method
    start_time = time.perf_counter()
    individual_result = individual_lookups()
    end_time = time.perf_counter()
    individual_time = end_time - start_time

    assert len(individual_result) == lookup_count
    individual_ops_per_second = lookup_count / individual_time

    # Calculate performance comparison
    speedup = individual_time / bulk_time
    time_savings_pct = (individual_time - bulk_time) / individual_time * 100

    # Use logging to display results (will show with -s flag or --log-cli-level=INFO)
    logger = logging.getLogger(__name__)
    logger.info(
        f"Benchmark results for {num_children} children, {lookup_count} lookups:"
    )
    logger.info(f"  Bulk method: {bulk_time:.4f}s ({bulk_ops_per_second:.2f} ops/sec)")
    logger.info(
        f"  Individual method: {individual_time:.4f}s ({individual_ops_per_second:.2f} ops/sec)"
    )
    logger.info(
        f"  Speedup: {speedup:.2f}x faster, {time_savings_pct:.1f}% time savings"
    )

    assert bulk_time > 0, "Bulk method should complete successfully"
    assert individual_time > 0, "Individual method should complete successfully"
    assert speedup >= 1.0, (
        f"Expected bulk method to be faster, but got {speedup:.2f}x speedup"
    )


class MockAdapter(BaseAdapter):
    """Implementation of BaseAdapter for testing"""

    async def _run(self, input):
        return RunOutput(output="test output", intermediate_outputs=None), None

    def adapter_name(self) -> str:
        return "test"


@pytest.fixture
def base_task():
    return Task(name="test_task", instruction="test_instruction")


@pytest.fixture
def adapter(base_task):
    return MockAdapter(
        task=base_task,
        run_config=RunConfigProperties(
            model_name="test_model",
            model_provider_name="openai",
            prompt_id="simple_prompt_builder",
            structured_output_mode="json_schema",
        ),
    )


async def test_invoke_parsing_flow(adapter):
    # Mock dependencies
    mock_provider = MagicMock()
    mock_provider.parser = "test_parser"
    mock_provider.formatter = None
    mock_provider.reasoning_capable = False

    mock_parser = MagicMock()
    mock_parser.parse_output.return_value = RunOutput(
        output="parsed test output", intermediate_outputs={"key": "value"}
    )

    with (
        patch.object(adapter, "model_provider", return_value=mock_provider),
        patch(
            "kiln_ai.adapters.model_adapters.base_adapter.model_parser_from_id",
            return_value=mock_parser,
        ),
        patch("kiln_ai.adapters.model_adapters.base_adapter.Config") as mock_config,
    ):
        # Disable autosaving for this test
        mock_config.shared.return_value.autosave_runs = False
        mock_config.shared.return_value.user_id = "test_user_id"

        # Execute
        result = await adapter.invoke("test input")

        # Verify parsing occurred
        mock_parser.parse_output.assert_called_once()
        parsed_args = mock_parser.parse_output.call_args[1]
        assert isinstance(parsed_args["original_output"], RunOutput)
        assert parsed_args["original_output"].output == "test output"

        # Verify result contains parsed output
        assert isinstance(result, TaskRun)
        assert result.output.output == "parsed test output"
        assert result.intermediate_outputs == {"key": "value"}
        assert result.input == "test input"

        # Test with reasoning required, that we error if no reasoning is returned
        mock_provider.reasoning_capable = True
        with pytest.raises(
            RuntimeError,
            match=r"^Reasoning is required for this model, but no reasoning was returned.$",
        ):
            await adapter.invoke("test input")


async def test_invoke_parsing_flow_basic_no_reasoning(adapter):
    """Test for reasoning_optional_for_structured_output
    when reasoning is not required.
    This is a special case where we want to return the output as is.
    """
    # Mock dependencies
    mock_provider = MagicMock()
    mock_provider.parser = "test_parser"
    mock_provider.formatter = None
    mock_provider.reasoning_capable = False
    mock_provider.reasoning_optional_for_structured_output = True

    mock_parser = MagicMock()
    mock_parser.parse_output.return_value = RunOutput(
        output="parsed test output", intermediate_outputs={"key": "value"}
    )

    with (
        patch.object(adapter, "model_provider", return_value=mock_provider),
        patch(
            "kiln_ai.adapters.model_adapters.base_adapter.model_parser_from_id",
            return_value=mock_parser,
        ),
        patch("kiln_ai.adapters.model_adapters.base_adapter.Config") as mock_config,
    ):
        # Disable autosaving for this test
        mock_config.shared.return_value.autosave_runs = False
        mock_config.shared.return_value.user_id = "test_user_id"

        # Execute
        result = await adapter.invoke("test input")

        # Verify parsing occurred
        mock_parser.parse_output.assert_called_once()
        parsed_args = mock_parser.parse_output.call_args[1]
        assert isinstance(parsed_args["original_output"], RunOutput)
        assert parsed_args["original_output"].output == "test output"

        # Verify result contains parsed output
        assert isinstance(result, TaskRun)
        assert result.output.output == "parsed test output"
        assert result.intermediate_outputs == {"key": "value"}
        assert result.input == "test input"


async def test_invoke_parsing_flow_no_reasoning_with_structured_output(adapter):
    """Test for reasoning_optional_for_structured_output
    when reasoning is required but not provided, with structured output enabled.
    This is a special case where we don't want to error, but we want to return the output as is.
    """
    # Mock dependencies
    mock_provider = MagicMock()
    mock_provider.parser = "test_parser"
    mock_provider.formatter = None
    mock_provider.reasoning_capable = True
    mock_provider.reasoning_optional_for_structured_output = True

    mock_parser = MagicMock()
    mock_parser.parse_output.return_value = RunOutput(
        output="parsed test output", intermediate_outputs={"key": "value"}
    )

    with (
        patch.object(adapter, "model_provider", return_value=mock_provider),
        patch(
            "kiln_ai.adapters.model_adapters.base_adapter.model_parser_from_id",
            return_value=mock_parser,
        ),
        patch("kiln_ai.adapters.model_adapters.base_adapter.Config") as mock_config,
        patch.object(adapter, "has_structured_output", return_value=True),
    ):
        # Disable autosaving for this test
        mock_config.shared.return_value.autosave_runs = False
        mock_config.shared.return_value.user_id = "test_user_id"

        # Execute
        result = await adapter.invoke("test input")

        # Verify parsing occurred
        mock_parser.parse_output.assert_called_once()
        parsed_args = mock_parser.parse_output.call_args[1]
        assert isinstance(parsed_args["original_output"], RunOutput)
        assert parsed_args["original_output"].output == "test output"

        # Verify result contains parsed output
        assert isinstance(result, TaskRun)
        assert result.output.output == "parsed test output"
        assert result.intermediate_outputs == {"key": "value"}
        assert result.input == "test input"


async def test_invoke_parsing_flow_with_reasoning_and_structured_output(adapter):
    """Test for reasoning_optional_for_structured_output
    when reasoning is provided with structured output enabled.
    This is a special case where we want to return the output as is.
    """
    # Mock dependencies
    mock_provider = MagicMock()
    mock_provider.parser = "test_parser"
    mock_provider.formatter = None
    mock_provider.reasoning_capable = True
    mock_provider.reasoning_optional_for_structured_output = True

    mock_parser = MagicMock()
    mock_parser.parse_output.return_value = RunOutput(
        output="parsed test output", intermediate_outputs={"reasoning": "value"}
    )

    with (
        patch.object(adapter, "model_provider", return_value=mock_provider),
        patch(
            "kiln_ai.adapters.model_adapters.base_adapter.model_parser_from_id",
            return_value=mock_parser,
        ),
        patch("kiln_ai.adapters.model_adapters.base_adapter.Config") as mock_config,
        patch.object(adapter, "has_structured_output", return_value=True),
    ):
        # Disable autosaving for this test
        mock_config.shared.return_value.autosave_runs = False
        mock_config.shared.return_value.user_id = "test_user_id"

        # Execute
        result = await adapter.invoke("test input")

        # Verify parsing occurred
        mock_parser.parse_output.assert_called_once()
        parsed_args = mock_parser.parse_output.call_args[1]
        assert isinstance(parsed_args["original_output"], RunOutput)
        assert parsed_args["original_output"].output == "test output"

        # Verify result contains parsed output
        assert isinstance(result, TaskRun)
        assert result.output.output == "parsed test output"
        assert result.intermediate_outputs == {"reasoning": "value"}
        assert result.input == "test input"
