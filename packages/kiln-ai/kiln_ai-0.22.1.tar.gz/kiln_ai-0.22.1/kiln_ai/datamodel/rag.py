from typing import TYPE_CHECKING, Union

from pydantic import Field, model_validator

from kiln_ai.datamodel.basemodel import ID_TYPE, FilenameString, KilnParentedModel
from kiln_ai.utils.validation import ToolNameString

if TYPE_CHECKING:
    from kiln_ai.datamodel.project import Project


class RagConfig(KilnParentedModel):
    name: FilenameString = Field(
        description="A name to identify this RAG configuration for your own reference.",
    )

    is_archived: bool = Field(
        default=False,
        description="Whether the RAG configuration is archived. Archived RAG configurations are not shown in the UI and are not available for use.",
    )

    description: str | None = Field(
        default=None,
        description="A description of the RAG configuration for you and your team. Will not be used in prompts/training/validation.",
    )

    tool_name: ToolNameString = Field(
        description="A name for the model to identify the Search Tool in conversations.",
    )

    tool_description: str = Field(
        description="A description of the purpose of the tool. The model will use this description to understand the tool's capabilities.",
        max_length=128,
    )

    extractor_config_id: ID_TYPE = Field(
        description="The ID of the extractor config used to extract the documents.",
    )

    chunker_config_id: ID_TYPE = Field(
        description="The ID of the chunker config used to chunk the documents.",
    )

    embedding_config_id: ID_TYPE = Field(
        description="The ID of the embedding config used to embed the documents.",
    )

    vector_store_config_id: ID_TYPE = Field(
        description="The ID of the vector store config used to store the documents.",
    )

    tags: list[str] | None = Field(
        default=None,
        description="List of document tags to filter by. If None, all documents in the project are used.",
    )

    # Workaround to return typed parent without importing Project
    def parent_project(self) -> Union["Project", None]:
        if self.parent is None or self.parent.__class__.__name__ != "Project":
            return None
        return self.parent  # type: ignore

    @model_validator(mode="after")
    def validate_tags(self):
        if self.tags is not None:
            if len(self.tags) == 0:
                raise ValueError("Tags cannot be an empty list.")
            for tag in self.tags:
                if not tag:
                    raise ValueError("Tags cannot be empty.")
                if " " in tag:
                    raise ValueError("Tags cannot contain spaces. Try underscores.")

        if self.tool_name.strip() == "":
            raise ValueError("Tool name cannot be empty.")
        if self.tool_description.strip() == "":
            raise ValueError("Tool description cannot be empty.")

        return self
