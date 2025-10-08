from typing import List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from kiln_ai.adapters.vector_store.base_vector_store_adapter import SearchResult
from kiln_ai.datamodel.embedding import EmbeddingConfig
from kiln_ai.datamodel.project import Project
from kiln_ai.datamodel.rag import RagConfig
from kiln_ai.datamodel.vector_store import VectorStoreConfig, VectorStoreType
from kiln_ai.tools.base_tool import ToolCallContext
from kiln_ai.tools.rag_tools import ChunkContext, RagTool, format_search_results


class TestChunkContext:
    """Test the ChunkContext model."""

    def test_chunk_context_serialize_basic(self):
        """Test basic serialization of ChunkContext."""
        chunk = ChunkContext(
            metadata={"document_id": "doc1", "chunk_idx": 0},
            text="This is test content.",
        )

        result = chunk.serialize()
        expected = "[document_id: doc1, chunk_idx: 0]\nThis is test content.\n\n"
        assert result == expected

    def test_chunk_context_serialize_empty_metadata(self):
        """Test serialization with empty metadata."""
        chunk = ChunkContext(metadata={}, text="Content without metadata.")

        result = chunk.serialize()
        expected = "[]\nContent without metadata.\n\n"
        assert result == expected

    def test_chunk_context_serialize_multiple_metadata(self):
        """Test serialization with multiple metadata fields."""
        chunk = ChunkContext(
            metadata={
                "document_id": "doc123",
                "chunk_idx": 5,
                "score": 0.95,
                "source": "file.txt",
            },
            text="Multi-metadata content.",
        )

        result = chunk.serialize()
        # Note: dict order might vary, so check that all parts are present
        assert "[" in result and "]" in result
        assert "document_id: doc123" in result
        assert "chunk_idx: 5" in result
        assert "score: 0.95" in result
        assert "source: file.txt" in result
        assert "\nMulti-metadata content.\n\n" in result

    def test_chunk_context_serialize_empty_text(self):
        """Test serialization with empty text."""
        chunk = ChunkContext(metadata={"document_id": "doc1"}, text="")

        result = chunk.serialize()
        expected = "[document_id: doc1]\n\n\n"
        assert result == expected


class TestFormatSearchResults:
    """Test the format_search_results function."""

    def test_format_search_results_single_result(self):
        """Test formatting a single search result."""
        search_results = [
            SearchResult(
                document_id="doc1",
                chunk_idx=0,
                chunk_text="First chunk content",
                similarity=0.95,
            )
        ]

        result = format_search_results(search_results)
        expected = "[document_id: doc1, chunk_idx: 0]\nFirst chunk content\n\n"
        assert result == expected

    def test_format_search_results_multiple_results(self):
        """Test formatting multiple search results."""
        search_results = [
            SearchResult(
                document_id="doc1",
                chunk_idx=0,
                chunk_text="First chunk",
                similarity=0.95,
            ),
            SearchResult(
                document_id="doc2",
                chunk_idx=1,
                chunk_text="Second chunk",
                similarity=0.85,
            ),
        ]

        result = format_search_results(search_results)

        # Check that both chunks are present and separated by the delimiter
        assert "[document_id: doc1, chunk_idx: 0]\nFirst chunk\n\n" in result
        assert "[document_id: doc2, chunk_idx: 1]\nSecond chunk\n\n" in result
        assert "\n=========\n" in result

    def test_format_search_results_empty_list(self):
        """Test formatting empty search results."""
        search_results: List[SearchResult] = []

        result = format_search_results(search_results)
        assert result == ""

    def test_format_search_results_preserves_search_result_data(self):
        """Test that formatting preserves all relevant SearchResult data."""
        search_results = [
            SearchResult(
                document_id="test_doc_123",
                chunk_idx=42,
                chunk_text="Complex text with\nmultiple lines\nand special chars!@#$%",
                similarity=0.7654321,
            )
        ]

        result = format_search_results(search_results)

        assert "document_id: test_doc_123" in result
        assert "chunk_idx: 42" in result
        assert "Complex text with\nmultiple lines\nand special chars!@#$%" in result
        # Note: similarity is not included in the formatted output, which matches the implementation


class TestRagTool:
    """Test the RagTool class."""

    @pytest.fixture
    def mock_rag_config(self):
        """Create a mock RAG config."""
        config = Mock(spec=RagConfig)
        config.id = "rag_config_123"
        config.tool_name = "Test Search Tool"
        config.tool_description = "A test search tool for RAG"
        config.vector_store_config_id = "vector_store_456"
        config.embedding_config_id = "embedding_789"
        return config

    @pytest.fixture
    def mock_project(self):
        """Create a mock project."""
        project = Mock(spec=Project)
        project.id = "project_123"
        project.path = "/test/project/path"
        return project

    @pytest.fixture
    def mock_vector_store_config(self):
        """Create a mock vector store config."""
        config = Mock(spec=VectorStoreConfig)
        config.id = "vector_store_456"
        config.store_type = VectorStoreType.LANCE_DB_VECTOR
        return config

    @pytest.fixture
    def mock_embedding_config(self):
        """Create a mock embedding config."""
        config = Mock(spec=EmbeddingConfig)
        config.id = "embedding_789"
        return config

    def test_rag_tool_init_success(self, mock_rag_config, mock_project):
        """Test successful RagTool initialization."""
        mock_rag_config.parent_project.return_value = mock_project

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vector_store_config = Mock(spec=VectorStoreConfig)
            mock_vs_config_class.from_id_and_parent_path.return_value = (
                mock_vector_store_config
            )

            tool = RagTool("tool_123", mock_rag_config)

            assert tool._id == "tool_123"
            assert tool._name == "Test Search Tool"
            assert tool._description == "A test search tool for RAG"
            assert tool._rag_config == mock_rag_config
            assert tool._vector_store_config == mock_vector_store_config
            assert tool._vector_store_adapter is None

            # Verify vector store config lookup
            mock_vs_config_class.from_id_and_parent_path.assert_called_once_with(
                "vector_store_456", "/test/project/path"
            )

    def test_rag_tool_init_vector_store_config_not_found(
        self, mock_rag_config, mock_project
    ):
        """Test RagTool initialization when vector store config is not found."""
        mock_rag_config.parent_project.return_value = mock_project

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = None

            with pytest.raises(
                ValueError, match="Vector store config not found: vector_store_456"
            ):
                RagTool("tool_123", mock_rag_config)

    def test_rag_tool_project_property(self, mock_rag_config, mock_project):
        """Test RagTool project cached property."""
        mock_rag_config.parent_project.return_value = mock_project

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_123", mock_rag_config)

            # Test that project property returns the correct project
            assert tool.project == mock_project

            # Test that it's cached (should not call parent_project again)
            assert tool.project == mock_project
            mock_rag_config.parent_project.assert_called_once()

    def test_rag_tool_project_property_no_project(self, mock_rag_config):
        """Test RagTool initialization when no project is found."""
        mock_rag_config.parent_project.return_value = None

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            # The constructor should fail when accessing the project property
            with pytest.raises(
                ValueError, match="RAG config rag_config_123 has no project"
            ):
                RagTool("tool_123", mock_rag_config)

    def test_rag_tool_embedding_property(
        self, mock_rag_config, mock_project, mock_embedding_config
    ):
        """Test RagTool embedding cached property."""
        mock_rag_config.parent_project.return_value = mock_project
        mock_embedding_adapter = Mock()

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch("kiln_ai.tools.rag_tools.EmbeddingConfig") as mock_embed_config_class,
            patch(
                "kiln_ai.tools.rag_tools.embedding_adapter_from_type"
            ) as mock_adapter_factory,
        ):
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()
            mock_embed_config_class.from_id_and_parent_path.return_value = (
                mock_embedding_config
            )
            mock_adapter_factory.return_value = mock_embedding_adapter

            tool = RagTool("tool_123", mock_rag_config)

            # Test that embedding property returns the correct tuple
            config, adapter = tool.embedding
            assert config == mock_embedding_config
            assert adapter == mock_embedding_adapter

            # Test that it's cached
            config2, adapter2 = tool.embedding
            assert config2 == mock_embedding_config
            assert adapter2 == mock_embedding_adapter

            # Verify calls
            mock_embed_config_class.from_id_and_parent_path.assert_called_once_with(
                "embedding_789", "/test/project/path"
            )
            mock_adapter_factory.assert_called_once_with(mock_embedding_config)

    def test_rag_tool_embedding_property_config_not_found(
        self, mock_rag_config, mock_project
    ):
        """Test RagTool embedding property when embedding config is not found."""
        mock_rag_config.parent_project.return_value = mock_project

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch("kiln_ai.tools.rag_tools.EmbeddingConfig") as mock_embed_config_class,
        ):
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()
            mock_embed_config_class.from_id_and_parent_path.return_value = None

            tool = RagTool("tool_123", mock_rag_config)

            with pytest.raises(
                ValueError, match="Embedding config not found: embedding_789"
            ):
                _ = tool.embedding

    async def test_rag_tool_vector_store_property(self, mock_rag_config, mock_project):
        """Test RagTool vector_store async property."""
        mock_rag_config.parent_project.return_value = mock_project
        mock_vector_store_adapter = AsyncMock()

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch(
                "kiln_ai.tools.rag_tools.vector_store_adapter_for_config",
                new_callable=AsyncMock,
            ) as mock_adapter_factory,
        ):
            mock_vector_store_config = Mock()
            mock_vs_config_class.from_id_and_parent_path.return_value = (
                mock_vector_store_config
            )
            mock_adapter_factory.return_value = mock_vector_store_adapter

            tool = RagTool("tool_123", mock_rag_config)

            # Test that vector_store property returns the correct adapter
            adapter = await tool.vector_store()
            assert adapter == mock_vector_store_adapter

            # Test that it's cached
            adapter2 = await tool.vector_store()
            assert adapter2 == mock_vector_store_adapter

            # Verify factory was called only once due to caching
            mock_adapter_factory.assert_called_once_with(
                vector_store_config=mock_vector_store_config, rag_config=mock_rag_config
            )

    async def test_rag_tool_interface_methods(self, mock_rag_config, mock_project):
        """Test RagTool interface methods: id, name, description, toolcall_definition."""
        mock_rag_config.parent_project.return_value = mock_project

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_123", mock_rag_config)

            # Test interface methods
            assert await tool.id() == "tool_123"
            assert await tool.name() == "Test Search Tool"
            description = await tool.description()
            assert description == "A test search tool for RAG"

            # Test toolcall_definition
            definition = await tool.toolcall_definition()
            expected_definition = {
                "type": "function",
                "function": {
                    "name": "Test Search Tool",
                    "description": "A test search tool for RAG",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query",
                            },
                        },
                        "required": ["query"],
                    },
                },
            }
            assert definition == expected_definition

    async def test_rag_tool_run_vector_store_type(self, mock_rag_config, mock_project):
        """Test RagTool.run() with LANCE_DB_VECTOR store type (embedding needed)."""
        mock_rag_config.parent_project.return_value = mock_project

        # Mock search results
        search_results = [
            SearchResult(
                document_id="doc1",
                chunk_idx=0,
                chunk_text="Test content 1",
                similarity=0.95,
            ),
            SearchResult(
                document_id="doc2",
                chunk_idx=1,
                chunk_text="Test content 2",
                similarity=0.85,
            ),
        ]

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch("kiln_ai.tools.rag_tools.EmbeddingConfig") as mock_embed_config_class,
            patch(
                "kiln_ai.tools.rag_tools.embedding_adapter_from_type"
            ) as mock_adapter_factory,
            patch(
                "kiln_ai.tools.rag_tools.vector_store_adapter_for_config",
                new_callable=AsyncMock,
            ) as mock_vs_adapter_factory,
        ):
            # Setup mocks
            mock_vector_store_config = Mock()
            mock_vector_store_config.store_type = VectorStoreType.LANCE_DB_VECTOR
            mock_vs_config_class.from_id_and_parent_path.return_value = (
                mock_vector_store_config
            )

            mock_embedding_config = Mock()
            mock_embed_config_class.from_id_and_parent_path.return_value = (
                mock_embedding_config
            )

            mock_embedding_adapter = AsyncMock()
            mock_embedding_result = Mock()
            mock_embedding_result.embeddings = [Mock(vector=[0.1, 0.2, 0.3, 0.4])]
            mock_embedding_adapter.generate_embeddings.return_value = (
                mock_embedding_result
            )
            mock_adapter_factory.return_value = mock_embedding_adapter

            mock_vector_store_adapter = AsyncMock()
            mock_vector_store_adapter.search.return_value = search_results
            mock_vs_adapter_factory.return_value = mock_vector_store_adapter

            tool = RagTool("tool_123", mock_rag_config)

            # Run the tool
            result = await tool.run(context=None, query="test query")

            # Verify the result format
            expected_result = (
                "[document_id: doc1, chunk_idx: 0]\nTest content 1\n\n"
                "\n=========\n"
                "[document_id: doc2, chunk_idx: 1]\nTest content 2\n\n"
            )
            assert result == expected_result

            # Verify embedding generation was called
            mock_embedding_adapter.generate_embeddings.assert_called_once_with(
                ["test query"]
            )

            # Verify vector store search was called correctly
            mock_vector_store_adapter.search.assert_called_once()
            search_query = mock_vector_store_adapter.search.call_args[0][0]
            assert search_query.query_string == "test query"
            assert search_query.query_embedding == [
                0.1,
                0.2,
                0.3,
                0.4,
            ]  # Embedding provided for VECTOR type

    async def test_rag_tool_run_hybrid_store_type(self, mock_rag_config, mock_project):
        """Test RagTool.run() with LANCE_DB_HYBRID store type (embedding needed)."""
        mock_rag_config.parent_project.return_value = mock_project

        # Mock embedding result
        mock_embedding_result = Mock()
        mock_embedding_result.embeddings = [Mock(vector=[0.1, 0.2, 0.3, 0.4])]

        # Mock search results
        search_results = [
            SearchResult(
                document_id="doc1",
                chunk_idx=0,
                chunk_text="Hybrid search result",
                similarity=0.92,
            )
        ]

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch("kiln_ai.tools.rag_tools.EmbeddingConfig") as mock_embed_config_class,
            patch(
                "kiln_ai.tools.rag_tools.embedding_adapter_from_type"
            ) as mock_adapter_factory,
            patch(
                "kiln_ai.tools.rag_tools.vector_store_adapter_for_config",
                new_callable=AsyncMock,
            ) as mock_vs_adapter_factory,
        ):
            # Setup mocks
            mock_vector_store_config = Mock()
            mock_vector_store_config.store_type = VectorStoreType.LANCE_DB_HYBRID
            mock_vs_config_class.from_id_and_parent_path.return_value = (
                mock_vector_store_config
            )

            mock_embedding_config = Mock()
            mock_embed_config_class.from_id_and_parent_path.return_value = (
                mock_embedding_config
            )

            mock_embedding_adapter = AsyncMock()
            mock_embedding_adapter.generate_embeddings.return_value = (
                mock_embedding_result
            )
            mock_adapter_factory.return_value = mock_embedding_adapter

            mock_vector_store_adapter = AsyncMock()
            mock_vector_store_adapter.search.return_value = search_results
            mock_vs_adapter_factory.return_value = mock_vector_store_adapter

            tool = RagTool("tool_123", mock_rag_config)

            # Run the tool
            result = await tool.run(context=None, query="hybrid query")

            # Verify embedding generation was called
            mock_embedding_adapter.generate_embeddings.assert_called_once_with(
                ["hybrid query"]
            )

            # Verify vector store search was called with embedding
            mock_vector_store_adapter.search.assert_called_once()
            search_query = mock_vector_store_adapter.search.call_args[0][0]
            assert search_query.query_string == "hybrid query"
            assert search_query.query_embedding == [0.1, 0.2, 0.3, 0.4]

            # Verify result
            expected_result = (
                "[document_id: doc1, chunk_idx: 0]\nHybrid search result\n\n"
            )
            assert result == expected_result

    async def test_rag_tool_run_fts_store_type(self, mock_rag_config, mock_project):
        """Test RagTool.run() with LANCE_DB_FTS store type (no embedding needed)."""
        mock_rag_config.parent_project.return_value = mock_project

        # Mock search results
        search_results = [
            SearchResult(
                document_id="doc_fts",
                chunk_idx=2,
                chunk_text="FTS search result",
                similarity=0.88,
            )
        ]

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch("kiln_ai.tools.rag_tools.EmbeddingConfig") as mock_embed_config_class,
            patch(
                "kiln_ai.tools.rag_tools.embedding_adapter_from_type"
            ) as mock_adapter_factory,
            patch(
                "kiln_ai.tools.rag_tools.vector_store_adapter_for_config",
                new_callable=AsyncMock,
            ) as mock_vs_adapter_factory,
        ):
            # Setup mocks
            mock_vector_store_config = Mock()
            mock_vector_store_config.store_type = VectorStoreType.LANCE_DB_FTS
            mock_vs_config_class.from_id_and_parent_path.return_value = (
                mock_vector_store_config
            )

            mock_embedding_config = Mock()
            mock_embed_config_class.from_id_and_parent_path.return_value = (
                mock_embedding_config
            )

            mock_embedding_adapter = AsyncMock()
            mock_adapter_factory.return_value = mock_embedding_adapter

            mock_vector_store_adapter = AsyncMock()
            mock_vector_store_adapter.search.return_value = search_results
            mock_vs_adapter_factory.return_value = mock_vector_store_adapter

            tool = RagTool("tool_123", mock_rag_config)

            # Run the tool
            result = await tool.run(context=None, query="fts query")

            # Verify the result format
            expected_result = (
                "[document_id: doc_fts, chunk_idx: 2]\nFTS search result\n\n"
            )
            assert result == expected_result

            # Verify embedding generation was NOT called for FTS
            mock_embedding_adapter.generate_embeddings.assert_not_called()

            # Verify vector store search was called without embedding
            mock_vector_store_adapter.search.assert_called_once()
            search_query = mock_vector_store_adapter.search.call_args[0][0]
            assert search_query.query_string == "fts query"
            assert search_query.query_embedding is None  # No embedding for FTS type

    async def test_rag_tool_run_no_embeddings_generated(
        self, mock_rag_config, mock_project
    ):
        """Test RagTool.run() when no embeddings are generated."""
        mock_rag_config.parent_project.return_value = mock_project

        # Mock empty embedding result
        mock_embedding_result = Mock()
        mock_embedding_result.embeddings = []

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch("kiln_ai.tools.rag_tools.EmbeddingConfig") as mock_embed_config_class,
            patch(
                "kiln_ai.tools.rag_tools.embedding_adapter_from_type"
            ) as mock_adapter_factory,
            patch(
                "kiln_ai.tools.rag_tools.vector_store_adapter_for_config",
                new_callable=AsyncMock,
            ) as mock_vs_adapter_factory,
        ):
            # Setup mocks
            mock_vector_store_config = Mock()
            mock_vector_store_config.store_type = VectorStoreType.LANCE_DB_HYBRID
            mock_vs_config_class.from_id_and_parent_path.return_value = (
                mock_vector_store_config
            )

            mock_embedding_config = Mock()
            mock_embed_config_class.from_id_and_parent_path.return_value = (
                mock_embedding_config
            )

            mock_embedding_adapter = AsyncMock()
            mock_embedding_adapter.generate_embeddings.return_value = (
                mock_embedding_result
            )
            mock_adapter_factory.return_value = mock_embedding_adapter

            mock_vector_store_adapter = AsyncMock()
            mock_vs_adapter_factory.return_value = mock_vector_store_adapter

            tool = RagTool("tool_123", mock_rag_config)

            # Run the tool and expect an error
            with pytest.raises(ValueError, match="No embeddings generated"):
                await tool.run(context=None, query="query with no embeddings")

    async def test_rag_tool_run_empty_search_results(
        self, mock_rag_config, mock_project
    ):
        """Test RagTool.run() with empty search results."""
        mock_rag_config.parent_project.return_value = mock_project

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch("kiln_ai.tools.rag_tools.EmbeddingConfig") as mock_embed_config_class,
            patch(
                "kiln_ai.tools.rag_tools.embedding_adapter_from_type"
            ) as mock_adapter_factory,
            patch(
                "kiln_ai.tools.rag_tools.vector_store_adapter_for_config",
                new_callable=AsyncMock,
            ) as mock_vs_adapter_factory,
        ):
            # Setup mocks
            mock_vector_store_config = Mock()
            mock_vector_store_config.store_type = VectorStoreType.LANCE_DB_VECTOR
            mock_vs_config_class.from_id_and_parent_path.return_value = (
                mock_vector_store_config
            )

            mock_embedding_config = Mock()
            mock_embed_config_class.from_id_and_parent_path.return_value = (
                mock_embedding_config
            )

            mock_embedding_adapter = AsyncMock()
            mock_embedding_result = Mock()
            mock_embedding_result.embeddings = [Mock(vector=[0.1, 0.2, 0.3, 0.4])]
            mock_embedding_adapter.generate_embeddings.return_value = (
                mock_embedding_result
            )
            mock_adapter_factory.return_value = mock_embedding_adapter

            mock_vector_store_adapter = AsyncMock()
            mock_vector_store_adapter.search.return_value = []  # Empty results
            mock_vs_adapter_factory.return_value = mock_vector_store_adapter

            tool = RagTool("tool_123", mock_rag_config)

            # Run the tool
            result = await tool.run(context=None, query="query with no results")

            # Should return empty string for no results
            assert result == ""

    async def test_rag_tool_run_with_context_is_accepted(
        self, mock_rag_config, mock_project
    ):
        """Ensure RagTool.run accepts and works when a ToolCallContext is provided."""
        mock_rag_config.parent_project.return_value = mock_project

        # Mock search results
        search_results = [
            SearchResult(
                document_id="doc_ctx",
                chunk_idx=3,
                chunk_text="Context ok",
                similarity=0.77,
            )
        ]

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
            patch("kiln_ai.tools.rag_tools.EmbeddingConfig") as mock_embed_config_class,
            patch(
                "kiln_ai.tools.rag_tools.embedding_adapter_from_type"
            ) as mock_adapter_factory,
            patch(
                "kiln_ai.tools.rag_tools.vector_store_adapter_for_config",
                new_callable=AsyncMock,
            ) as mock_vs_adapter_factory,
        ):
            # VECTOR type → embedding path taken
            mock_vector_store_config = Mock()
            mock_vector_store_config.store_type = VectorStoreType.LANCE_DB_VECTOR
            mock_vs_config_class.from_id_and_parent_path.return_value = (
                mock_vector_store_config
            )

            mock_embedding_config = Mock()
            mock_embed_config_class.from_id_and_parent_path.return_value = (
                mock_embedding_config
            )

            mock_embedding_adapter = AsyncMock()
            mock_embedding_result = Mock()
            mock_embedding_result.embeddings = [Mock(vector=[1.0])]
            mock_embedding_adapter.generate_embeddings.return_value = (
                mock_embedding_result
            )
            mock_adapter_factory.return_value = mock_embedding_adapter

            mock_vector_store_adapter = AsyncMock()
            mock_vector_store_adapter.search.return_value = search_results
            mock_vs_adapter_factory.return_value = mock_vector_store_adapter

            tool = RagTool("tool_ctx", mock_rag_config)

            ctx = ToolCallContext(allow_saving=False)
            result = await tool.run(context=ctx, query="with context")

            # Works and returns formatted text
            assert result == "[document_id: doc_ctx, chunk_idx: 3]\nContext ok\n\n"

            # Normal behavior still occurs
            mock_embedding_adapter.generate_embeddings.assert_called_once_with(
                ["with context"]
            )
            mock_vector_store_adapter.search.assert_called_once()

    async def test_rag_tool_run_missing_query_raises(
        self, mock_rag_config, mock_project
    ):
        """Ensure RagTool.run enforces the 'if not query' guard."""
        mock_rag_config.parent_project.return_value = mock_project

        with (
            patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class,
        ):
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()
            tool = RagTool("tool_err", mock_rag_config)

            with pytest.raises(KeyError, match="query"):
                await tool.run(context=None)


class TestRagToolNameAndDescription:
    """Test RagTool name and description functionality with tool_name and tool_description fields."""

    @pytest.fixture
    def mock_rag_config_with_tool_fields(self):
        """Create a mock RAG config with specific tool_name and tool_description."""
        config = Mock(spec=RagConfig)
        config.id = "rag_config_456"
        config.tool_name = "Advanced Document Search"
        config.tool_description = "An advanced search tool that retrieves relevant documents from the knowledge base using semantic similarity"
        config.vector_store_config_id = "vector_store_789"
        config.embedding_config_id = "embedding_101"
        return config

    @pytest.fixture
    def mock_project_for_tool_fields(self):
        """Create a mock project for tool field tests."""
        project = Mock(spec=Project)
        project.id = "project_456"
        project.path = "/test/tool/project"
        return project

    def test_rag_tool_uses_tool_name_field(
        self, mock_rag_config_with_tool_fields, mock_project_for_tool_fields
    ):
        """Test that RagTool uses the tool_name field from RagConfig."""
        mock_rag_config_with_tool_fields.parent_project.return_value = (
            mock_project_for_tool_fields
        )

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_456", mock_rag_config_with_tool_fields)

            assert tool._name == "Advanced Document Search"

    def test_rag_tool_uses_tool_description_field(
        self, mock_rag_config_with_tool_fields, mock_project_for_tool_fields
    ):
        """Test that RagTool uses the tool_description field from RagConfig."""
        mock_rag_config_with_tool_fields.parent_project.return_value = (
            mock_project_for_tool_fields
        )

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_456", mock_rag_config_with_tool_fields)

            assert (
                tool._description
                == "An advanced search tool that retrieves relevant documents from the knowledge base using semantic similarity"
            )

    async def test_rag_tool_name_method_returns_tool_name(
        self, mock_rag_config_with_tool_fields, mock_project_for_tool_fields
    ):
        """Test that the name() method returns the tool_name field."""
        mock_rag_config_with_tool_fields.parent_project.return_value = (
            mock_project_for_tool_fields
        )

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_456", mock_rag_config_with_tool_fields)

            name = await tool.name()
            assert name == "Advanced Document Search"

    async def test_rag_tool_description_method_returns_tool_description(
        self, mock_rag_config_with_tool_fields, mock_project_for_tool_fields
    ):
        """Test that the description() method returns the tool_description field."""
        mock_rag_config_with_tool_fields.parent_project.return_value = (
            mock_project_for_tool_fields
        )

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_456", mock_rag_config_with_tool_fields)

            description = await tool.description()
            assert (
                description
                == "An advanced search tool that retrieves relevant documents from the knowledge base using semantic similarity"
            )

    async def test_rag_tool_toolcall_definition_uses_tool_fields(
        self, mock_rag_config_with_tool_fields, mock_project_for_tool_fields
    ):
        """Test that toolcall_definition uses tool_name and tool_description fields."""
        mock_rag_config_with_tool_fields.parent_project.return_value = (
            mock_project_for_tool_fields
        )

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_456", mock_rag_config_with_tool_fields)

            definition = await tool.toolcall_definition()

            expected_definition = {
                "type": "function",
                "function": {
                    "name": "Advanced Document Search",
                    "description": "An advanced search tool that retrieves relevant documents from the knowledge base using semantic similarity",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query",
                            },
                        },
                        "required": ["query"],
                    },
                },
            }

            assert definition == expected_definition

    def test_rag_tool_with_unicode_tool_fields(self, mock_project_for_tool_fields):
        """Test RagTool with Unicode characters in tool_name and tool_description."""
        config = Mock(spec=RagConfig)
        config.id = "rag_config_unicode"
        config.tool_name = "🔍 文档搜索工具"
        config.tool_description = "一个用于搜索文档的高级工具 🚀"
        config.vector_store_config_id = "vector_store_789"
        config.embedding_config_id = "embedding_101"
        config.parent_project.return_value = mock_project_for_tool_fields

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_unicode", config)
            assert tool._name == "🔍 文档搜索工具"
            assert tool._description == "一个用于搜索文档的高级工具 🚀"

    def test_rag_tool_with_multiline_tool_description(
        self, mock_project_for_tool_fields
    ):
        """Test RagTool with multiline tool_description."""
        multiline_description = """This is a comprehensive search tool that:
- Searches through document collections
- Uses semantic similarity matching
- Returns relevant context with metadata
- Supports various document formats"""

        config = Mock(spec=RagConfig)
        config.id = "rag_config_multiline"
        config.tool_name = "Comprehensive Search Tool"
        config.tool_description = multiline_description
        config.vector_store_config_id = "vector_store_789"
        config.embedding_config_id = "embedding_101"
        config.parent_project.return_value = mock_project_for_tool_fields

        with patch("kiln_ai.tools.rag_tools.VectorStoreConfig") as mock_vs_config_class:
            mock_vs_config_class.from_id_and_parent_path.return_value = Mock()

            tool = RagTool("tool_multiline", config)
            assert tool._description == multiline_description
