import filecmp
import hashlib
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import patch

import pytest
from pydantic import BaseModel, Field, SerializationInfo, field_serializer

from conftest import MockFileFactoryMimeType
from kiln_ai.datamodel.basemodel import KilnAttachmentModel, KilnBaseModel


class ModelWithAttachment(KilnBaseModel):
    attachment: KilnAttachmentModel | None = Field(default=None)
    attachment_list: Optional[List[KilnAttachmentModel]] = Field(default=None)
    attachment_dict: Optional[Dict[str, KilnAttachmentModel]] = Field(default=None)


class ContainerModel(BaseModel):
    indirect_attachment: Optional[KilnAttachmentModel] = Field(default=None)
    indirect_attachment_list: Optional[List[KilnAttachmentModel]] = Field(default=None)
    indirect_attachment_dict: Optional[Dict[str, KilnAttachmentModel]] = Field(
        default=None
    )


class ModelWithIndirectAttachment(KilnBaseModel):
    # this nested model contains an attachment field
    container: ContainerModel = Field(default=ContainerModel())
    container_optional: Optional[ContainerModel] = Field(default=None)


def hash_file(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


@pytest.fixture
def test_base_kiln_file(tmp_path) -> Path:
    test_file_path = tmp_path / "test_model.json"
    data = {"v": 1, "model_type": "kiln_base_model"}

    with open(test_file_path, "w") as file:
        json.dump(data, file, indent=4)

    return test_file_path


def test_save_to_file_with_attachment_single(test_base_kiln_file, mock_file_factory):
    test_file = mock_file_factory(MockFileFactoryMimeType.PDF)
    model = ModelWithAttachment(
        path=test_base_kiln_file,
        attachment=KilnAttachmentModel.from_file(test_file),
    )

    assert model.attachment.path is None

    model.save_to_file()

    assert model.attachment.path is not None

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    # the path after saving
    attachment_path = data["attachment"]["path"]

    # check it is a string, and not an absolute path
    assert isinstance(attachment_path, str)
    assert not Path(attachment_path).is_absolute()

    # check persisted path is relative to model.path.parent
    assert model.path is not None
    expected_full_path = model.path.parent / attachment_path
    assert expected_full_path.exists()
    assert filecmp.cmp(expected_full_path, test_file)


def test_save_to_file_with_attachment_list(test_base_kiln_file, mock_file_factory):
    media_file_paths = [
        mock_file_factory(MockFileFactoryMimeType.PDF),
        mock_file_factory(MockFileFactoryMimeType.PNG),
        mock_file_factory(MockFileFactoryMimeType.MP4),
        mock_file_factory(MockFileFactoryMimeType.OGG),
    ]

    # we map hashes to their files, so we can find the corresponding file after the save
    media_file_hashes = {hash_file(p): p for p in media_file_paths}

    model = ModelWithAttachment(
        path=test_base_kiln_file,
        attachment_list=[KilnAttachmentModel.from_file(p) for p in media_file_paths],
    )

    for attachment in model.attachment_list:
        assert attachment.path is None

    model.save_to_file()

    for attachment in model.attachment_list:
        assert attachment.path is not None

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    # check the paths are relative to model.path.parent
    for attachment in data["attachment_list"]:
        attachment_path = attachment["path"]
        assert isinstance(attachment_path, str)
        assert not Path(attachment_path).is_absolute()

    # check all the files were persisted
    attachment_list = data["attachment_list"]
    assert len(attachment_list) == len(media_file_paths)

    # check the files are present and correct in model.path.parent
    for attachment in attachment_list:
        attachment_path = attachment["path"]
        # check the path is a string, and not an absolute path
        assert isinstance(attachment_path, str)
        assert not Path(attachment_path).is_absolute()

        # check the file is the same as the original
        assert model.path is not None
        expected_full_path = model.path.parent / attachment_path
        assert expected_full_path.exists()

        # find the original file it corresponds to, and check content hash is identical
        original_file = media_file_hashes[hash_file(expected_full_path)]
        assert filecmp.cmp(expected_full_path, original_file)


def test_save_to_file_with_attachment_dict(test_base_kiln_file, mock_file_factory):
    media_file_paths = [
        mock_file_factory(MockFileFactoryMimeType.PDF),
        mock_file_factory(MockFileFactoryMimeType.PNG),
        mock_file_factory(MockFileFactoryMimeType.MP4),
        mock_file_factory(MockFileFactoryMimeType.OGG),
    ]
    # we map hashes to their files, so we can find the corresponding file after the save
    media_file_hashes = {hash_file(p): p for p in media_file_paths}

    attachment_dict = {
        f"file_{i}": KilnAttachmentModel.from_file(p)
        for i, p in enumerate(media_file_paths)
    }
    model = ModelWithAttachment(
        path=test_base_kiln_file,
        attachment_dict=attachment_dict,
    )
    for attachment in model.attachment_dict.values():
        assert attachment.path is None

    model.save_to_file()

    for attachment in model.attachment_dict.values():
        assert attachment.path is not None

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    # check the paths are relative to model.path.parent
    for attachment in data["attachment_dict"].values():
        attachment_path = attachment["path"]
        assert isinstance(attachment_path, str)
        assert not Path(attachment_path).is_absolute()

    # check all the files were persisted
    attachment_dict = data["attachment_dict"]
    assert len(attachment_dict) == len(media_file_paths)

    # check the files are present and correct in model.path.parent
    for attachment in attachment_dict.values():
        attachment_path = attachment["path"]
        # check the path is a string, and not an absolute path
        assert isinstance(attachment_path, str)
        assert not Path(attachment_path).is_absolute()

        # check the file is the same as the original
        assert model.path is not None
        expected_full_path = model.path.parent / attachment_path
        assert expected_full_path.exists()

        # find the original file it corresponds to, and check content hash is identical
        original_file = media_file_hashes[hash_file(expected_full_path)]
        assert filecmp.cmp(expected_full_path, original_file)


def test_save_to_file_with_indirect_attachment(test_base_kiln_file, mock_file_factory):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    model = ModelWithIndirectAttachment(
        path=test_base_kiln_file,
        container=ContainerModel(
            indirect_attachment=KilnAttachmentModel.from_file(test_media_file_document)
        ),
    )
    assert model.container.indirect_attachment.path is None

    model.save_to_file()

    assert model.container.indirect_attachment.path is not None

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    # check the path is relative to model.path.parent
    assert isinstance(data["container"]["indirect_attachment"]["path"], str)
    assert not Path(data["container"]["indirect_attachment"]["path"]).is_absolute()

    # check the file is the same as the original
    assert model.path is not None
    expected_full_path = (
        model.path.parent / data["container"]["indirect_attachment"]["path"]
    )
    assert expected_full_path.exists()
    assert filecmp.cmp(expected_full_path, test_media_file_document)


def test_save_to_file_with_indirect_attachment_optional(
    test_base_kiln_file, mock_file_factory
):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    model = ModelWithIndirectAttachment(
        path=test_base_kiln_file,
        container_optional=ContainerModel(
            indirect_attachment=KilnAttachmentModel.from_file(test_media_file_document)
        ),
    )
    assert model.container_optional.indirect_attachment.path is None

    model.save_to_file()

    assert model.container_optional.indirect_attachment.path is not None

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    # check the path is relative to model.path.parent
    assert data["container_optional"] is not None

    # check the file is the same as the original
    assert model.path is not None
    expected_full_path = (
        model.path.parent / data["container_optional"]["indirect_attachment"]["path"]
    )
    assert expected_full_path.exists()
    assert filecmp.cmp(expected_full_path, test_media_file_document)


def test_save_to_file_with_indirect_attachment_optional_none(test_base_kiln_file):
    # check we don't copy the attachment if it is None
    with patch.object(KilnAttachmentModel, "copy_file_to") as mock_save_to_file:
        mock_save_to_file.return_value = Path("fake.txt")
        model = ModelWithIndirectAttachment(
            path=test_base_kiln_file,
            container_optional=None,
        )
        model.save_to_file()

        with open(test_base_kiln_file, "r") as file:
            data = json.load(file)

        # check the path is relative to model.path.parent
        assert data["container_optional"] is None

        # check KilnAttachmentModel.copy_to() not called
        mock_save_to_file.assert_not_called()


def test_dump_dest_path(test_base_kiln_file, mock_file_factory):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    model = ModelWithAttachment(
        path=test_base_kiln_file,
        attachment=KilnAttachmentModel.from_file(test_media_file_document),
    )

    with pytest.raises(
        ValueError,
        match="dest_path must be a valid Path object when saving attachments",
    ):
        model.model_dump_json(context={"save_attachments": True})

    # should raise when dest_path is not a Path object
    with pytest.raises(
        ValueError,
        match="dest_path must be a valid Path object when saving attachments",
    ):
        model.model_dump_json(
            context={
                "save_attachments": True,
                "dest_path": str(test_media_file_document),
            }
        )

    # should raise when dest_path is not a directory
    with pytest.raises(
        ValueError,
        match="dest_path must be a directory when saving attachments",
    ):
        model.model_dump_json(
            context={"save_attachments": True, "dest_path": test_media_file_document}
        )

    # should not raise when dest_path is set
    model.model_dump_json(context={"dest_path": test_base_kiln_file.parent})


def test_resolve_path(test_base_kiln_file, mock_file_factory):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    model = ModelWithAttachment(
        path=test_base_kiln_file,
        attachment=KilnAttachmentModel.from_file(test_media_file_document),
    )
    assert (
        model.attachment.resolve_path(test_base_kiln_file.parent)
        == test_media_file_document
    )


def test_create_from_data(test_base_kiln_file, mock_file_factory):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    with open(test_media_file_document, "rb") as file:
        data = file.read()

    attachment = KilnAttachmentModel.from_data(data, "application/pdf")
    assert attachment.resolve_path(test_base_kiln_file.parent).exists()

    model = ModelWithAttachment(
        path=test_base_kiln_file,
        attachment=attachment,
    )
    assert model.attachment.path is None

    model.save_to_file()

    assert model.attachment.path is not None

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    assert str(data["attachment"]["path"]) == str(model.attachment.path)
    assert filecmp.cmp(
        test_media_file_document, attachment.resolve_path(test_base_kiln_file.parent)
    )


def test_attachment_file_does_not_exist(test_base_kiln_file):
    not_found_file = Path(f"/not/found/{uuid.uuid4()!s}.txt")

    # should raise when we assign a file that does not exist
    with pytest.raises(ValueError):
        KilnAttachmentModel.from_file(not_found_file)


def test_attachment_is_folder(test_base_kiln_file, tmp_path):
    # create folder in tmp_path
    folder = tmp_path / "test_folder"
    folder.mkdir()

    # should raise when we assign a folder
    with pytest.raises(ValueError):
        ModelWithAttachment(
            path=test_base_kiln_file,
            attachment=KilnAttachmentModel.from_file(folder),
        )


@pytest.mark.parametrize(
    "mime_type",
    [
        MockFileFactoryMimeType.PDF,
        MockFileFactoryMimeType.PNG,
        MockFileFactoryMimeType.MP4,
        MockFileFactoryMimeType.OGG,
    ],
)
def test_attachment_lifecycle(test_base_kiln_file, mock_file_factory, mime_type):
    test_media_file_document = mock_file_factory(mime_type)
    model = ModelWithAttachment(
        path=test_base_kiln_file,
        attachment=KilnAttachmentModel.from_file(test_media_file_document),
    )

    # before save, the attachment has an absolute path and its stable path does not exist yet
    assert model.attachment.input_path is not None
    assert model.attachment.path is None

    # before save, resolve_path should resolve to the original absolute path
    path_resolved_pre_saved = model.attachment.resolve_path(test_base_kiln_file.parent)
    assert path_resolved_pre_saved is not None
    assert filecmp.cmp(path_resolved_pre_saved, test_media_file_document)

    # check it also returns the absolute path when we don't provide the parent path
    path_resolved_pre_saved_no_parent = model.attachment.resolve_path()
    assert path_resolved_pre_saved_no_parent is not None
    assert filecmp.cmp(path_resolved_pre_saved_no_parent, test_media_file_document)

    assert path_resolved_pre_saved_no_parent == path_resolved_pre_saved

    # now we save the model, the attachment is persisted to disk, the absolute path is cleared,
    # and the stable path (relative to the model's path) is set
    model.save_to_file()

    # after save, the attachment has a stable path and its absolute path is cleared
    assert model.attachment.path is not None
    assert model.attachment.input_path is None

    # when we load the model from file, the attachment has its stable relative path, and no absolute path
    model_loaded_from_file = ModelWithAttachment.load_from_file(test_base_kiln_file)
    assert model_loaded_from_file.attachment.path is not None
    assert model_loaded_from_file.attachment.input_path is None

    # the attachment is not aware of its full absolute path, so we need to resolve it, and it should reconstruct it
    path_resolved_post_saved = model_loaded_from_file.attachment.resolve_path(
        test_base_kiln_file.parent
    )
    assert path_resolved_post_saved is not None
    assert filecmp.cmp(path_resolved_post_saved, test_media_file_document)

    # verify the model JSON file does not contain the input_path
    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)
    assert "input_path" not in data["attachment"]
    assert "path" in data["attachment"]

    # test idempotency - saving again should not change the attachment path
    model.save_to_file()
    assert model.attachment.path is not None
    assert model.attachment.path == Path(data["attachment"]["path"])

    model_loaded_from_file = ModelWithAttachment.load_from_file(test_base_kiln_file)
    assert model_loaded_from_file.attachment.path is not None
    assert model_loaded_from_file.attachment.input_path is None
    assert model_loaded_from_file.attachment.path == Path(data["attachment"]["path"])
    assert filecmp.cmp(
        model_loaded_from_file.attachment.resolve_path(test_base_kiln_file.parent),
        test_media_file_document,
    )


def test_attachment_rejects_relative_path_input(mock_file_factory):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    # the input path should be absolute, and we should reject relative paths
    with pytest.raises(ValueError):
        KilnAttachmentModel.from_file(
            test_media_file_document.relative_to(test_media_file_document.parent)
        )


def test_loading_from_file(test_base_kiln_file, mock_file_factory):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    root_path = test_base_kiln_file.parent
    json_path = root_path / "test_model.json"
    model = ModelWithAttachment(
        path=json_path,
        attachment=KilnAttachmentModel.from_file(test_media_file_document),
    )
    assert model.attachment.path is None

    model.save_to_file()

    assert model.attachment.path is not None

    # check we can load the model from the file
    model = ModelWithAttachment.load_from_file(json_path)

    assert model.attachment.path is not None

    # when we load from JSON, the attachment path is only the relative segment
    assert filecmp.cmp(root_path / model.attachment.path, test_media_file_document)

    # we need to make sure that the path is hydrated correctly so the next save
    # won't think the file does not exist during validation
    model.save_to_file()

    assert model.attachment.path is not None


class ModelWithAttachmentNameOverride(KilnBaseModel):
    attachment: KilnAttachmentModel = Field(default=None)

    @field_serializer("attachment")
    def serialize_attachment(
        self, attachment: KilnAttachmentModel, info: SerializationInfo
    ) -> dict:
        context = info.context or {}
        context["filename_prefix"] = "attachment_override"
        return attachment.model_dump(mode="json", context=context)


def test_attachment_filename_override(test_base_kiln_file, mock_file_factory):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    root_path = test_base_kiln_file.parent
    json_path = root_path / "test_model.json"
    model = ModelWithAttachmentNameOverride(
        path=json_path,
        attachment=KilnAttachmentModel.from_file(test_media_file_document),
    )

    model.save_to_file()

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    # file persisted to disk will be named like: attachment_override_<random_numbers>.pdf
    assert data["attachment"]["path"].startswith("attachment_override_")
    assert data["attachment"]["path"].endswith(".pdf")
    assert filecmp.cmp(root_path / data["attachment"]["path"], test_media_file_document)


class ModelWithAttachmentNameOverrideList(KilnBaseModel):
    attachment_list: List[KilnAttachmentModel] = Field(default=[])

    @field_serializer("attachment_list")
    def serialize_attachment_list(
        self, attachment_list: List[KilnAttachmentModel], info: SerializationInfo
    ) -> List[dict]:
        context = info.context or {}
        context["filename_prefix"] = "attachment_override"
        return [
            attachment.model_dump(mode="json", context=context)
            for attachment in attachment_list
        ]


def test_attachment_filename_override_list(test_base_kiln_file, mock_file_factory):
    test_media_file_paths = [
        mock_file_factory(MockFileFactoryMimeType.PDF),
        mock_file_factory(MockFileFactoryMimeType.PNG),
        mock_file_factory(MockFileFactoryMimeType.MP4),
        mock_file_factory(MockFileFactoryMimeType.OGG),
    ]
    root_path = test_base_kiln_file.parent
    json_path = root_path / "test_model.json"
    model = ModelWithAttachmentNameOverrideList(
        path=json_path,
        attachment_list=[
            KilnAttachmentModel.from_file(p) for p in test_media_file_paths
        ],
    )

    model.save_to_file()

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    for attachment, file_path in zip(data["attachment_list"], test_media_file_paths):
        # file persisted to disk will be named like: attachment_override_<random_numbers>.pdf
        assert attachment["path"].startswith("attachment_override_")
        extension = file_path.suffix
        assert attachment["path"].endswith(extension)
        assert filecmp.cmp(root_path / attachment["path"], file_path)


class ModelWithAttachmentNoNameOverride(KilnBaseModel):
    attachment: KilnAttachmentModel | None = Field(default=None)


def test_attachment_filename_no_override(test_base_kiln_file, mock_file_factory):
    test_media_file_document = mock_file_factory(MockFileFactoryMimeType.PDF)
    root_path = test_base_kiln_file.parent
    json_path = root_path / "test_model.json"
    model = ModelWithAttachmentNoNameOverride(
        path=json_path,
        attachment=KilnAttachmentModel.from_file(test_media_file_document),
    )

    model.save_to_file()

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    # file persisted to disk will be named like: <random_numbers>.pdf
    assert data["attachment"]["path"].split(".")[0].isdigit()
    assert data["attachment"]["path"].endswith(".pdf")
    assert filecmp.cmp(root_path / data["attachment"]["path"], test_media_file_document)


@pytest.mark.parametrize(
    "mime_type, extension",
    [
        (MockFileFactoryMimeType.PDF, ".pdf"),
        (MockFileFactoryMimeType.PNG, ".png"),
        (MockFileFactoryMimeType.MP4, ".mp4"),
        (MockFileFactoryMimeType.OGG, ".ogg"),
        (MockFileFactoryMimeType.MD, ".md"),
        (MockFileFactoryMimeType.TXT, ".txt"),
        (MockFileFactoryMimeType.HTML, ".html"),
        (MockFileFactoryMimeType.CSV, ".csv"),
        (MockFileFactoryMimeType.JPEG, ".jpeg"),
        (MockFileFactoryMimeType.MP3, ".mp3"),
        (MockFileFactoryMimeType.WAV, ".wav"),
        (MockFileFactoryMimeType.OGG, ".ogg"),
        (MockFileFactoryMimeType.MOV, ".mov"),
    ],
)
def test_attachment_extension_from_data(
    test_base_kiln_file, mock_file_factory, mime_type, extension
):
    test_media_file_document = mock_file_factory(mime_type)
    root_path = test_base_kiln_file.parent
    json_path = root_path / "test_model.json"

    data_bytes = test_media_file_document.read_bytes()

    model = ModelWithAttachment(
        path=json_path,
        attachment=KilnAttachmentModel.from_data(data_bytes, mime_type),
    )
    model.save_to_file()

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    assert data["attachment"]["path"].endswith(extension), (
        f"{data['attachment']['path']} does not end with {extension}"
    )
    assert filecmp.cmp(root_path / data["attachment"]["path"], test_media_file_document)


@pytest.mark.parametrize(
    "mime_type, extension",
    [
        ("application/octet-stream", ".unknown"),
        ("fake-mimetype", ".unknown"),
    ],
)
def test_attachment_extension_from_data_unknown_mime_type(
    test_base_kiln_file, mock_file_factory, mime_type, extension
):
    root_path = test_base_kiln_file.parent
    json_path = root_path / "test_model.json"

    data_bytes = b"fake data"

    model = ModelWithAttachment(
        path=json_path,
        attachment=KilnAttachmentModel.from_data(data_bytes, mime_type),
    )
    model.save_to_file()

    with open(test_base_kiln_file, "r") as file:
        data = json.load(file)

    assert data["attachment"]["path"].endswith(extension), (
        f"{data['attachment']['path']} does not end with {extension}"
    )
