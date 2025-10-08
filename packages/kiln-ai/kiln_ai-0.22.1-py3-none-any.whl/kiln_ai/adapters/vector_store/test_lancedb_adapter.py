import asyncio
import os
import random
import uuid
from pathlib import Path
from typing import Callable, List
from unittest.mock import patch

import pytest
from llama_index.core.schema import MetadataMode, NodeRelationship
from llama_index.core.vector_stores.types import VectorStoreQueryResult
from llama_index.vector_stores.lancedb.base import TableNotFoundError

from kiln_ai.adapters.vector_store.base_vector_store_adapter import (
    DocumentWithChunksAndEmbeddings,
    SearchResult,
    VectorStoreQuery,
)
from kiln_ai.adapters.vector_store.lancedb_adapter import LanceDBAdapter
from kiln_ai.adapters.vector_store.lancedb_helpers import deterministic_chunk_id
from kiln_ai.adapters.vector_store.vector_store_registry import (
    vector_store_adapter_for_config,
)
from kiln_ai.datamodel.basemodel import KilnAttachmentModel
from kiln_ai.datamodel.chunk import Chunk, ChunkedDocument
from kiln_ai.datamodel.datamodel_enums import ModelProviderName
from kiln_ai.datamodel.embedding import ChunkEmbeddings, Embedding, EmbeddingConfig
from kiln_ai.datamodel.rag import RagConfig
from kiln_ai.datamodel.vector_store import VectorStoreConfig, VectorStoreType
from kiln_ai.utils.config import Config


def get_all_nodes(adapter: LanceDBAdapter) -> List[SearchResult]:
    nodes = adapter.lancedb_vector_store.get_nodes()
    return [
        SearchResult(
            document_id=node.metadata["kiln_doc_id"],
            chunk_idx=node.metadata["kiln_chunk_idx"],
            chunk_text=node.get_content(MetadataMode.NONE),
            similarity=None,
        )
        for node in nodes
    ]


@pytest.fixture(autouse=True)
def patch_settings_dir(tmp_path):
    with patch("kiln_ai.utils.config.Config.settings_dir", return_value=tmp_path):
        yield


@pytest.fixture
def hybrid_vector_store_config():
    """Create a vector store config for testing."""
    return VectorStoreConfig(
        name="test_config",
        store_type=VectorStoreType.LANCE_DB_HYBRID,
        properties={
            "similarity_top_k": 10,
            "nprobes": 10,
            "overfetch_factor": 10,
            "vector_column_name": "vector",
            "text_key": "text",
            "doc_id_key": "doc_id",
        },
    )


@pytest.fixture
def fts_vector_store_config():
    """Create a vector store config for testing."""
    return VectorStoreConfig(
        name="test_config",
        store_type=VectorStoreType.LANCE_DB_FTS,
        properties={
            "similarity_top_k": 10,
            "overfetch_factor": 10,
            "vector_column_name": "vector",
            "text_key": "text",
            "doc_id_key": "doc_id",
        },
    )


@pytest.fixture
def knn_vector_store_config():
    """Create a vector store config for testing."""
    return VectorStoreConfig(
        name="test_config",
        store_type=VectorStoreType.LANCE_DB_VECTOR,
        properties={
            "similarity_top_k": 10,
            "nprobes": 10,
            "overfetch_factor": 10,
            "vector_column_name": "vector",
            "text_key": "text",
            "doc_id_key": "doc_id",
        },
    )


@pytest.fixture
def embedding_config():
    """Create an embedding config for testing."""
    return EmbeddingConfig(
        name="test_embedding",
        model_provider_name=ModelProviderName.openai,
        model_name="text-embedding-ada-002",
        properties={},
    )


@pytest.fixture
def create_rag_config_factory() -> Callable[
    [VectorStoreConfig, EmbeddingConfig], RagConfig
]:
    def create_rag_config(
        vector_store_config: VectorStoreConfig, embedding_config: EmbeddingConfig
    ) -> RagConfig:
        return RagConfig(
            name="test_rag",
            tool_name="test_rag_tool",
            tool_description="A test RAG tool for vector search",
            extractor_config_id="test_extractor",
            chunker_config_id="test_chunker",
            embedding_config_id=embedding_config.id,
            vector_store_config_id=vector_store_config.id,
        )

    return create_rag_config


def dicts_to_indexable_docs(
    docs: dict[str, list[dict[str, str | list[float]]]], tmp_path: Path
) -> list[DocumentWithChunksAndEmbeddings]:
    results = []
    for doc_id, doc in docs.items():
        chunked_documents = ChunkedDocument(
            chunker_config_id="test_chunker",
            chunks=[],
            path=tmp_path / "chunked_document.kiln",
        )
        chunk_embeddings = ChunkEmbeddings(
            embedding_config_id="test_embedding",
            embeddings=[],
            path=tmp_path / "chunk_embeddings.kiln",
        )
        for part in doc:
            # Ensure vector is a list of floats
            vector = part["vector"]
            if isinstance(vector, list):
                vector = [float(x) for x in vector]
            else:
                vector = [float(vector)]

            chunk_embeddings.embeddings.append(Embedding(vector=vector))
            chunked_documents.chunks.append(
                Chunk(
                    content=KilnAttachmentModel.from_data(
                        str(part["text"]),
                        "text/plain",
                    )
                )
            )
        results.append(
            DocumentWithChunksAndEmbeddings(
                document_id=doc_id,
                chunked_document=chunked_documents,
                chunk_embeddings=chunk_embeddings,
            )
        )

    return results


@pytest.fixture
def mock_chunked_documents(tmp_path):
    """Create sample chunks for testing."""
    docs: dict[str, list[dict[str, str | list[float]]]] = {
        "doc_001": [
            {
                "vector": [1.1, 1.2],
                "text": "The population of Tokyo, Japan is approximately 37 million people",
            },
            {
                "vector": [0.2, 1.8],
                "text": "New York City, USA has a population of about 8.8 million residents",
            },
            {
                "vector": [0.45452, 51.8],
                "text": "London, UK has a population of roughly 9 million people",
            },
            {
                "vector": [0.7, 0.8],
                "text": "Rio de Janeiro, Brazil has a population of about 6.7 million residents",
            },
        ],
        "doc_002": [
            {
                "vector": [50.0, 50.0],
                "text": "The area of Tokyo, Japan is approximately 2,191 square kilometers",
            },
            {
                "vector": [55.0, 55.0],
                "text": "The area of New York City, USA is approximately 783.8 square kilometers",
            },
            {
                "vector": [60.0, 60.0],
                "text": "The area of London, UK is approximately 1,572 square kilometers",
            },
            {
                "vector": [65.0, 65.0],
                "text": "The area of Rio de Janeiro, Brazil is approximately 1,256 square kilometers",
            },
        ],
    }

    return dicts_to_indexable_docs(docs, tmp_path)


@pytest.mark.asyncio
async def test_add_chunks_with_embeddings_and_similarity_search(
    knn_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test adding chunks and similarity search."""

    rag_config = create_rag_config_factory(knn_vector_store_config, embedding_config)

    # Create adapter using the registry
    adapter = await vector_store_adapter_for_config(rag_config, knn_vector_store_config)

    # Add chunks to the vector store
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Test similarity search - search for a vector close to [55.0, 55.0] (NYC area chunk)
    query_vector = [55.0, 55.0]

    results = await adapter.search(VectorStoreQuery(query_embedding=query_vector))

    # The closest should be NYC area chunk with vector [55.0, 55.0]
    assert len(results) > 0
    assert "New York City" in results[0].chunk_text
    assert "783.8 square kilometers" in results[0].chunk_text


@pytest.mark.asyncio
async def test_fts_search(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test full-text search functionality."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = await vector_store_adapter_for_config(rag_config, fts_vector_store_config)

    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    assert isinstance(adapter, LanceDBAdapter)

    # Test FTS search for "London"
    query_text = "london"

    results = await adapter.search(VectorStoreQuery(query_string=query_text))

    # Should find both London chunks
    assert len(results) >= 2
    london_texts = [result.chunk_text for result in results]
    assert any("London, UK has a population" in text for text in london_texts)
    assert any("The area of London, UK" in text for text in london_texts)


@pytest.mark.asyncio
async def test_hybrid_search(
    hybrid_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test hybrid search combining vector and text search."""
    rag_config = create_rag_config_factory(hybrid_vector_store_config, embedding_config)

    adapter = await vector_store_adapter_for_config(
        rag_config, hybrid_vector_store_config
    )

    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Test hybrid search - combine text "Tokyo" with vector close to Tokyo population vector [1.1, 1.2]
    query_text = "Tokyo"
    query_vector = [1.1, 1.2]

    results = await adapter.search(
        VectorStoreQuery(query_string=query_text, query_embedding=query_vector)
    )

    # Should find Tokyo-related chunks, with population chunk being highly ranked
    assert len(results) > 0
    tokyo_results = [result for result in results if "Tokyo" in result.chunk_text]
    assert len(tokyo_results) >= 2  # Both Tokyo chunks should be found


async def test_upsert_behavior(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test that adding the same chunks multiple times works (upsert behavior)."""

    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = await vector_store_adapter_for_config(rag_config, fts_vector_store_config)

    # Extract first document only
    first_doc = [mock_chunked_documents[0]]

    await adapter.add_chunks_with_embeddings(first_doc)

    # Search to verify it's there
    results1 = await adapter.search(VectorStoreQuery(query_string="Tokyo"))

    # Add the same document again
    await adapter.add_chunks_with_embeddings(first_doc)

    # Search again - should still find the same chunks (not duplicated)
    results2 = await adapter.search(VectorStoreQuery(query_string="Tokyo"))

    # Should find Tokyo chunks but behavior may vary based on LanceDB implementation
    assert len(results2) == len(results1)

    # Add all documents
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Final search
    results3 = await adapter.search(VectorStoreQuery(query_string="population"))

    assert len(results3) > 0


@pytest.mark.asyncio
async def test_count_records_empty_store(
    fts_vector_store_config, embedding_config, create_rag_config_factory
):
    """Test counting records in an empty vector store."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = await vector_store_adapter_for_config(rag_config, fts_vector_store_config)

    assert await adapter.count_records() == 0


@pytest.mark.asyncio
async def test_count_records_with_data(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test counting records after adding data."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = await vector_store_adapter_for_config(rag_config, fts_vector_store_config)

    # Add chunks first to create the table
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Should now have records (8 chunks total across both documents)
    final_count = await adapter.count_records()
    assert final_count == 8


@pytest.mark.asyncio
async def test_get_all_chunks(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test getting all chunks from the vector store."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Add chunks first to create the table
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Get all chunks
    all_chunks = get_all_nodes(adapter)
    assert len(all_chunks) == 8  # 8 chunks total

    # Verify structure
    for chunk in all_chunks:
        assert chunk.document_id in ["doc_001", "doc_002"]
        assert len(chunk.chunk_text) > 0
        assert chunk.similarity is None  # get_all_chunks doesn't include similarity


def test_format_query_result_error_conditions(
    fts_vector_store_config, embedding_config, create_rag_config_factory
):
    """Test error handling in format_query_result method."""

    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    # Create adapter with minimal setup
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Test with None ids - should return empty list instead of raising error
    query_result = VectorStoreQueryResult(ids=None, nodes=[], similarities=[])
    result = adapter.format_query_result(query_result)
    assert result == []

    # Test with None nodes - should return empty list instead of raising error
    query_result = VectorStoreQueryResult(ids=[], nodes=None, similarities=[])
    result = adapter.format_query_result(query_result)
    assert result == []

    # Test with None similarities - should return empty list instead of raising error
    query_result = VectorStoreQueryResult(ids=[], nodes=[], similarities=None)
    result = adapter.format_query_result(query_result)
    assert result == []

    # Test with empty lists - should return empty list (valid empty result)
    query_result = VectorStoreQueryResult(ids=[], nodes=[], similarities=[])
    result = adapter.format_query_result(query_result)
    assert result == []

    # Test with mismatched lengths where some arrays are empty - should return empty list
    query_result = VectorStoreQueryResult(ids=["1", "2"], nodes=[], similarities=[])
    with pytest.raises(
        ValueError, match="ids, nodes, and similarities must have the same length"
    ):
        adapter.format_query_result(query_result)

    # Test with mismatched lengths where all arrays are non-empty - should raise ValueError
    from llama_index.core.schema import TextNode

    node1 = TextNode(text="test1")
    query_result = VectorStoreQueryResult(
        ids=["1", "2"], nodes=[node1], similarities=[0.5, 0.3]
    )
    with pytest.raises(
        ValueError, match="ids, nodes, and similarities must have the same length"
    ):
        adapter.format_query_result(query_result)


def test_build_kwargs_for_query_validation_errors(
    create_rag_config_factory,
    hybrid_vector_store_config,
    fts_vector_store_config,
    knn_vector_store_config,
    embedding_config,
):
    """Test error handling in build_kwargs_for_query method."""

    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Test FTS search without query_string
    query = VectorStoreQuery(query_string=None, query_embedding=None)
    with pytest.raises(
        ValueError, match="query_string must be provided for fts search"
    ):
        adapter.build_kwargs_for_query(query)

    # Test HYBRID search without required parameters
    adapter = LanceDBAdapter(rag_config, hybrid_vector_store_config)

    query = VectorStoreQuery(query_string=None, query_embedding=[1.0, 2.0])
    with pytest.raises(
        ValueError,
        match="query_string and query_embedding must be provided for hybrid search",
    ):
        adapter.build_kwargs_for_query(query)

    query = VectorStoreQuery(query_string="test", query_embedding=None)
    with pytest.raises(
        ValueError,
        match="query_string and query_embedding must be provided for hybrid search",
    ):
        adapter.build_kwargs_for_query(query)

    # Test VECTOR search without embedding
    adapter = LanceDBAdapter(rag_config, knn_vector_store_config)

    query = VectorStoreQuery(query_string=None, query_embedding=None)
    with pytest.raises(
        ValueError, match="query_embedding must be provided for vector search"
    ):
        adapter.build_kwargs_for_query(query)


@pytest.mark.asyncio
async def test_search_with_table_not_found_error(
    fts_vector_store_config, embedding_config, create_rag_config_factory
):
    """Test that search handles TableNotFoundError gracefully"""

    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    # Create the adapter normally
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Mock the aquery method directly on the LanceDBVectorStore class
    with patch.object(adapter.lancedb_vector_store.__class__, "aquery") as mock_aquery:
        mock_aquery.side_effect = TableNotFoundError("Table vectors is not initialized")

        # Search should return empty list instead of raising error
        query = VectorStoreQuery(query_string="test query")
        results = await adapter.search(query)

        assert results == []


@pytest.mark.asyncio
async def test_search_with_empty_results_error(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
):
    """Test that search handles 'query results are empty' error gracefully"""

    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    # Create the adapter normally
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Search should return empty list instead of raising error
    query = VectorStoreQuery(query_string="test query")
    results = await adapter.search(query)

    assert results == []


async def test_destroy(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test the destroy method removes the database directory."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(
        rag_config,
        fts_vector_store_config,
    )

    # Add some data to create the database
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Verify data exists
    count = await adapter.count_records()
    assert count == 8

    # Get the database path
    db_path = LanceDBAdapter.lancedb_path_for_config(rag_config)
    assert os.path.exists(db_path)

    # Destroy the database
    await adapter.destroy()

    # Verify the database directory is gone
    assert not os.path.exists(db_path)


def test_lancedb_path_for_config():
    """Test the lancedb_path_for_config static method."""
    # Test with valid rag_config
    rag_config = RagConfig(
        name="test_rag",
        tool_name="test_rag_tool",
        tool_description="A test RAG tool for path testing",
        extractor_config_id="test_extractor",
        chunker_config_id="test_chunker",
        embedding_config_id="test_embedding",
        vector_store_config_id="test_vector_store",
    )

    expected_path = str(
        Path(Config.settings_dir()) / "rag_indexes" / "lancedb" / str(rag_config.id)
    )
    actual_path = LanceDBAdapter.lancedb_path_for_config(rag_config)

    assert actual_path == expected_path

    # Test with rag_config with no ID (should raise ValueError)
    rag_config_no_id = RagConfig(
        name="test_rag",
        tool_name="test_rag_tool",
        tool_description="A test RAG tool with no ID",
        extractor_config_id="test_extractor",
        chunker_config_id="test_chunker",
        embedding_config_id="test_embedding",
        vector_store_config_id="test_vector_store",
    )
    rag_config_no_id.id = None

    with pytest.raises(ValueError, match="Vector store config ID is required"):
        LanceDBAdapter.lancedb_path_for_config(rag_config_no_id)


def test_query_type_property(
    embedding_config,
    create_rag_config_factory,
):
    """Test the query_type property returns correct values for different store types."""

    # Test FTS query type
    fts_config = VectorStoreConfig(
        name="fts_test",
        store_type=VectorStoreType.LANCE_DB_FTS,
        properties={
            "similarity_top_k": 10,
            "overfetch_factor": 10,
            "vector_column_name": "vector",
            "text_key": "text",
            "doc_id_key": "doc_id",
        },
    )
    rag_config = create_rag_config_factory(fts_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_config)
    assert adapter.query_type == "fts"

    # Test Hybrid query type
    hybrid_config = VectorStoreConfig(
        name="hybrid_test",
        store_type=VectorStoreType.LANCE_DB_HYBRID,
        properties={
            "similarity_top_k": 10,
            "nprobes": 10,
            "overfetch_factor": 10,
            "vector_column_name": "vector",
            "text_key": "text",
            "doc_id_key": "doc_id",
        },
    )
    rag_config = create_rag_config_factory(hybrid_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, hybrid_config)
    assert adapter.query_type == "hybrid"

    # Test Vector query type
    vector_config = VectorStoreConfig(
        name="vector_test",
        store_type=VectorStoreType.LANCE_DB_VECTOR,
        properties={
            "similarity_top_k": 10,
            "nprobes": 10,
            "overfetch_factor": 10,
            "vector_column_name": "vector",
            "text_key": "text",
            "doc_id_key": "doc_id",
        },
    )
    rag_config = create_rag_config_factory(vector_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, vector_config)
    assert adapter.query_type == "vector"


@pytest.mark.asyncio
async def test_adapter_reuse_preserves_data(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test that creating the same LanceDBAdapter twice doesn't destroy/empty the db."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    # Create first adapter and add data
    adapter1 = LanceDBAdapter(rag_config, fts_vector_store_config)
    await adapter1.add_chunks_with_embeddings([mock_chunked_documents[0]])

    # Verify data exists
    count1 = await adapter1.count_records()
    assert count1 == 4

    # Create second adapter with same config
    adapter2 = LanceDBAdapter(rag_config, fts_vector_store_config)
    await adapter2.add_chunks_with_embeddings([mock_chunked_documents[1]])

    # Verify data still exists and wasn't destroyed by second instantiation
    count2 = await adapter2.count_records()
    assert count2 == 8

    # interesting: adapter1 is no longer usable after creating adapter2
    # with pytest.raises(
    #     Exception,
    #     match="lance error: Retryable commit conflict for version 4: This CreateIndex transaction was preempted by concurrent transaction Rewrite at version 4. Please retry.",
    # ):
    await adapter1.search(VectorStoreQuery(query_string="Tokyo"))

    # but we can query adapter2
    results2 = await adapter2.search(VectorStoreQuery(query_string="Tokyo"))
    assert len(results2) > 0


@pytest.mark.asyncio
async def test_skip_existing_chunks_when_count_matches(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test that chunks already in DB are skipped when they match incoming chunks count."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Add first document
    first_doc = [mock_chunked_documents[0]]  # doc_001 with 4 chunks
    await adapter.add_chunks_with_embeddings(first_doc)

    # Verify it was added
    count_after_first = await adapter.count_records()
    assert count_after_first == 4

    # Try to add the same document again - should be skipped
    await adapter.add_chunks_with_embeddings(first_doc)

    # Count should remain the same (chunks were skipped)
    count_after_second = await adapter.count_records()
    assert count_after_second == 4

    # Verify the chunks are still there and retrievable
    results = await adapter.search(VectorStoreQuery(query_string="Tokyo"))
    assert len(results) > 0
    assert "Tokyo" in results[0].chunk_text


@pytest.mark.asyncio
async def test_batching_functionality(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Test basic batching functionality in add_chunks_with_embeddings."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Create a document with many chunks to test batching
    large_doc_data = {
        "large_doc": [
            {"vector": [i * 0.1, i * 0.2], "text": f"Chunk {i} content"}
            for i in range(15)  # 15 chunks to test batching
        ]
    }

    large_doc_records = dicts_to_indexable_docs(large_doc_data, tmp_path)

    # Track batch sizes by patching the insert method
    batch_sizes = []

    async def mock_async_add(self, nodes, **kwargs):
        batch_sizes.append(len(nodes))
        return self.add(nodes, **kwargs)

    # Patch the async_add method at the class level
    with patch.object(
        adapter.lancedb_vector_store.__class__, "async_add", mock_async_add
    ):
        # Add with small batch size to force batching
        await adapter.add_chunks_with_embeddings(large_doc_records, nodes_batch_size=5)

    # Verify batching behavior
    # With 15 chunks and batch_size=5, we expect 3 batches of 5 chunks each
    expected_batch_sizes = [5, 5, 5]
    assert batch_sizes == expected_batch_sizes, (
        f"Expected batch sizes {expected_batch_sizes}, got {batch_sizes}"
    )

    # Verify all chunks were added
    count = await adapter.count_records()
    assert count == 15

    # Verify we can search and find chunks
    results = await adapter.search(VectorStoreQuery(query_string="Chunk"))
    assert len(results) > 0  # Should find chunks containing "Chunk"
    assert len(results) <= 15  # Should not exceed total number of chunks


@pytest.mark.asyncio
async def test_batching_functionality_with_remainder(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Test batching functionality with a remainder (not evenly divisible)."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Create a document with 17 chunks to test batching with remainder
    large_doc_data = {
        "large_doc": [
            {"vector": [i * 0.1, i * 0.2], "text": f"Chunk {i} content"}
            for i in range(17)  # 17 chunks to test batching with remainder
        ]
    }

    large_doc_records = dicts_to_indexable_docs(large_doc_data, tmp_path)

    # Track batch sizes by patching the insert method
    batch_sizes = []

    async def mock_async_add(self, nodes, **kwargs):
        batch_sizes.append(len(nodes))
        return self.add(nodes, **kwargs)

    # Patch the async_add method at the class level
    with patch.object(
        adapter.lancedb_vector_store.__class__, "async_add", mock_async_add
    ):
        # Add with batch_size=7 to get 2 full batches + 1 remainder batch
        await adapter.add_chunks_with_embeddings(large_doc_records, nodes_batch_size=7)

    # Verify batching behavior
    # With 17 chunks and batch_size=7, we expect 2 batches of 7 and 1 batch of 3
    expected_batch_sizes = [7, 7, 3]
    assert batch_sizes == expected_batch_sizes, (
        f"Expected batch sizes {expected_batch_sizes}, got {batch_sizes}"
    )

    # Verify all chunks were added
    count = await adapter.count_records()
    assert count == 17


@pytest.mark.asyncio
async def test_batching_functionality_edge_cases(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Test batching functionality edge cases (small batches, single batch)."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Test 1: Single batch (3 chunks with batch_size=10)
    small_doc_data = {
        "small_doc": [
            {"vector": [i * 0.1, i * 0.2], "text": f"Small chunk {i} content"}
            for i in range(3)
        ]
    }

    small_doc_records = dicts_to_indexable_docs(small_doc_data, tmp_path)

    # Track batch sizes by patching the insert method
    batch_sizes = []

    async def mock_async_add(self, nodes, **kwargs):
        batch_sizes.append(len(nodes))
        return self.add(nodes, **kwargs)

    # Test single batch scenario
    with patch.object(
        adapter.lancedb_vector_store.__class__, "async_add", mock_async_add
    ):
        await adapter.add_chunks_with_embeddings(small_doc_records, nodes_batch_size=10)

    # With 3 chunks and batch_size=10, we expect 1 batch of 3 chunks
    expected_batch_sizes = [3]
    assert batch_sizes == expected_batch_sizes, (
        f"Expected batch sizes {expected_batch_sizes}, got {batch_sizes}"
    )

    # Verify all chunks were added
    count = await adapter.count_records()
    assert count == 3

    # Test 2: Very small batches (batch_size=1)
    batch_sizes.clear()  # Reset for next test

    # Create new rag_config to get a fresh database
    rag_config2 = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter2 = LanceDBAdapter(rag_config2, fts_vector_store_config)

    with patch.object(
        adapter2.lancedb_vector_store.__class__, "async_add", mock_async_add
    ):
        await adapter2.add_chunks_with_embeddings(small_doc_records, nodes_batch_size=1)

    # With 3 chunks and batch_size=1, we expect 3 batches of 1 chunk each
    expected_batch_sizes = [1, 1, 1]
    assert batch_sizes == expected_batch_sizes, (
        f"Expected batch sizes {expected_batch_sizes}, got {batch_sizes}"
    )


@pytest.mark.asyncio
async def test_get_nodes_by_ids_functionality(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Test get_nodes_by_ids method functionality."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # before inserting data, we should simply return an empty list
    retrieved_nodes_before_any_insert = await adapter.get_nodes_by_ids(
        [str(uuid.uuid4()), str(uuid.uuid4())]
    )
    assert len(retrieved_nodes_before_any_insert) == 0

    # Add some data
    await adapter.add_chunks_with_embeddings([mock_chunked_documents[0]])  # doc_001

    # Test getting nodes by IDs - compute expected IDs
    expected_ids = [deterministic_chunk_id("doc_001", i) for i in range(4)]

    # Get nodes by IDs
    retrieved_nodes = await adapter.get_nodes_by_ids(expected_ids)

    # Should retrieve all 4 nodes
    assert len(retrieved_nodes) == 4

    # Verify node properties
    for i, node in enumerate(retrieved_nodes):
        assert node.id_ == expected_ids[i]
        assert node.metadata["kiln_doc_id"] == "doc_001"
        assert node.metadata["kiln_chunk_idx"] == i
        assert len(node.get_content()) > 0

    # Test with non-existent IDs
    fake_ids = [deterministic_chunk_id("fake_doc", i) for i in range(2)]
    retrieved_fake = await adapter.get_nodes_by_ids(fake_ids)
    assert len(retrieved_fake) == 0

    # Test with empty table (no table exists yet)
    empty_rag_config = create_rag_config_factory(
        fts_vector_store_config, embedding_config
    )
    empty_adapter = LanceDBAdapter(empty_rag_config, fts_vector_store_config)
    empty_result = await empty_adapter.get_nodes_by_ids(expected_ids)
    assert len(empty_result) == 0


@pytest.mark.asyncio
async def test_delete_nodes_by_document_id(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test delete_nodes_by_document_id method."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Add both documents
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Verify both documents are there
    count_before = await adapter.count_records()
    assert count_before == 8  # 4 chunks per document

    # Delete nodes for doc_001
    await adapter.delete_nodes_by_document_id("doc_001")

    # Verify doc_001 chunks are gone
    count_after = await adapter.count_records()
    assert count_after == 4  # Only doc_002 chunks remain

    # Verify we can still find doc_002 chunks but not doc_001
    results_doc2 = await adapter.search(VectorStoreQuery(query_string="area"))
    assert len(results_doc2) > 0

    # Try to search for population (which was in doc_001) - should find no results
    # LanceDB raises a Warning when no results are found, so we catch it
    try:
        results_doc1 = await adapter.search(VectorStoreQuery(query_string="population"))
        assert len(results_doc1) == 0
    except Warning as w:
        # This is expected - LanceDB raises a Warning for empty results
        assert "query results are empty" in str(w)

    # Try to delete non-existent document (should not error)
    await adapter.delete_nodes_by_document_id("non_existent_doc")
    final_count = await adapter.count_records()
    assert final_count == 4  # Count unchanged


@pytest.mark.asyncio
async def test_uuid_scheme_retrieval_and_node_properties(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test UUID scheme retrieval and that inserted nodes have correct ID and ref_doc_id."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)

    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Add first document
    await adapter.add_chunks_with_embeddings([mock_chunked_documents[0]])  # doc_001

    # Test the UUID scheme: document_id::chunk_idx
    for chunk_idx in range(4):
        # Compute expected ID using the same scheme as the adapter
        expected_id = deterministic_chunk_id("doc_001", chunk_idx)

        # Retrieve the specific node by ID
        retrieved_nodes = await adapter.get_nodes_by_ids([expected_id])
        assert len(retrieved_nodes) == 1

        node = retrieved_nodes[0]

        # Test that inserted nodes have the expected ID we set
        assert node.id_ == expected_id

        # Test that inserted nodes have ref_doc_id set correctly
        # The ref_doc_id should be set through the SOURCE relationship
        source_relationship = node.relationships.get(NodeRelationship.SOURCE)
        assert source_relationship is not None
        # Handle both single RelatedNodeInfo and list of RelatedNodeInfo
        if isinstance(source_relationship, list):
            assert len(source_relationship) > 0
            assert source_relationship[0].node_id == "doc_001"
        else:
            assert source_relationship.node_id == "doc_001"

        # Verify other node properties
        assert node.metadata["kiln_doc_id"] == "doc_001"
        assert node.metadata["kiln_chunk_idx"] == chunk_idx
        assert len(node.get_content()) > 0
        assert node.embedding is not None
        assert len(node.embedding) == 2  # Our test embeddings are 2D

    # Test with a different document to ensure the scheme works consistently
    await adapter.add_chunks_with_embeddings([mock_chunked_documents[1]])  # doc_002

    # Test retrieval of doc_002 chunks
    for chunk_idx in range(4):
        expected_id = deterministic_chunk_id("doc_002", chunk_idx)
        retrieved_nodes = await adapter.get_nodes_by_ids([expected_id])
        assert len(retrieved_nodes) == 1

        node = retrieved_nodes[0]
        assert node.id_ == expected_id
        assert node.metadata["kiln_doc_id"] == "doc_002"
        assert node.metadata["kiln_chunk_idx"] == chunk_idx

        # Check ref_doc_id relationship
        source_relationship = node.relationships.get(NodeRelationship.SOURCE)
        assert source_relationship is not None
        # Handle both single RelatedNodeInfo and list of RelatedNodeInfo
        if isinstance(source_relationship, list):
            assert len(source_relationship) > 0
            assert source_relationship[0].node_id == "doc_002"
        else:
            assert source_relationship.node_id == "doc_002"


@pytest.mark.asyncio
async def test_deterministic_chunk_id_consistency(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
):
    """Test that the deterministic chunk ID generation is consistent."""

    # Test that the same document_id and chunk_idx always produce the same UUID
    doc_id = "test_doc_123"
    chunk_idx = 5

    id1 = deterministic_chunk_id(doc_id, chunk_idx)
    id2 = deterministic_chunk_id(doc_id, chunk_idx)

    assert id1 == id2

    # Test that different inputs produce different UUIDs
    id3 = deterministic_chunk_id(doc_id, chunk_idx + 1)
    id4 = deterministic_chunk_id(doc_id + "_different", chunk_idx)

    assert id1 != id3
    assert id1 != id4
    assert id3 != id4

    # Verify the format is a valid UUID string
    import uuid

    try:
        uuid.UUID(id1)  # Should not raise an exception
        uuid.UUID(id3)
        uuid.UUID(id4)
    except ValueError:
        pytest.fail("Generated IDs are not valid UUIDs")


@pytest.mark.asyncio
async def test_chunk_replacement_triggers_deletion(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Test that adding different chunks for the same document triggers deletion of old chunks."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Create initial document with 2 chunks
    initial_doc_data = {
        "test_doc": [
            {"vector": [1.0, 1.0], "text": "Initial chunk 1"},
            {"vector": [2.0, 2.0], "text": "Initial chunk 2"},
        ]
    }
    initial_records = dicts_to_indexable_docs(initial_doc_data, tmp_path)

    # Add initial chunks
    await adapter.add_chunks_with_embeddings(initial_records)

    # Verify initial chunks are there
    initial_count = await adapter.count_records()
    assert initial_count == 2

    # Create modified document with 3 different chunks (more chunks than original)
    # This will trigger deletion because len(chunk_ids_in_database) != chunk_count_for_document (2 != 3)
    modified_doc_data = {
        "test_doc": [
            {"vector": [10.0, 10.0], "text": "Modified chunk 1"},
            {"vector": [20.0, 20.0], "text": "Modified chunk 2"},
            {"vector": [30.0, 30.0], "text": "Modified chunk 3"},
        ]
    }
    modified_records = dicts_to_indexable_docs(modified_doc_data, tmp_path)

    # Mock the delete_nodes_by_document_id method to verify it gets called
    delete_called = []
    original_delete = adapter.delete_nodes_by_document_id

    async def mock_delete(document_id: str):
        delete_called.append(document_id)
        return await original_delete(document_id)

    adapter.delete_nodes_by_document_id = mock_delete

    # Add modified chunks - this should trigger deletion of old chunks
    await adapter.add_chunks_with_embeddings(modified_records)

    # Verify delete was called for the document
    assert "test_doc" in delete_called

    # Verify final count is correct (only 2 new chunks)
    final_count = await adapter.count_records()
    assert final_count == 3

    # Verify the chunks are the new ones, not the old ones
    results = await adapter.search(VectorStoreQuery(query_string="Modified"))
    assert len(results) == 3
    assert all("Modified" in result.chunk_text for result in results)

    # Verify old chunks are gone - LanceDB raises a Warning for empty results
    try:
        old_results = await adapter.search(VectorStoreQuery(query_string="Initial"))
        assert len(old_results) == 0
    except Warning as w:
        # This is expected - LanceDB raises a Warning for empty results
        assert "query results are empty" in str(w)


@pytest.mark.asyncio
async def test_chunk_deletion_ensures_complete_cleanup_and_other_docs_unaffected(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Test that deletion completely cleans up all old chunks and other documents are unaffected."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Create initial document with 5 chunks
    initial_doc_data = {
        "target_doc": [
            {"vector": [1.0, 1.0], "text": "Original chunk 1"},
            {"vector": [2.0, 2.0], "text": "Original chunk 2"},
            {"vector": [3.0, 3.0], "text": "Original chunk 3"},
            {"vector": [4.0, 4.0], "text": "Original chunk 4"},
            {"vector": [5.0, 5.0], "text": "Original chunk 5"},
        ]
    }
    initial_records = dicts_to_indexable_docs(initial_doc_data, tmp_path)

    # Create another document that should remain unaffected
    other_doc_data = {
        "other_doc": [
            {"vector": [10.0, 10.0], "text": "Other doc chunk 1"},
            {"vector": [20.0, 20.0], "text": "Other doc chunk 2"},
            {"vector": [30.0, 30.0], "text": "Other doc chunk 3"},
        ]
    }
    other_records = dicts_to_indexable_docs(other_doc_data, tmp_path)

    # Add both documents
    await adapter.add_chunks_with_embeddings(initial_records)
    await adapter.add_chunks_with_embeddings(other_records)

    # Verify both documents are there (5 + 3 = 8 chunks)
    initial_count = await adapter.count_records()
    assert initial_count == 8

    # Verify we can find chunks from both documents
    target_results = await adapter.search(VectorStoreQuery(query_string="Original"))
    assert len(target_results) == 5

    other_results = await adapter.search(VectorStoreQuery(query_string="Other"))
    assert len(other_results) == 3

    # Create modified target document with 7 chunks (more than the original 5)
    # This will trigger deletion because len(chunk_ids_in_database) != chunk_count_for_document (5 != 7)
    # After deletion, we'll have 7 new chunks, demonstrating that the old 5 chunks were completely removed
    modified_doc_data = {
        "target_doc": [
            {"vector": [100.0, 100.0], "text": "New target chunk 1"},
            {"vector": [200.0, 200.0], "text": "New target chunk 2"},
            {"vector": [300.0, 300.0], "text": "New target chunk 3"},
            {"vector": [400.0, 400.0], "text": "New target chunk 4"},
            {"vector": [500.0, 500.0], "text": "New target chunk 5"},
            {"vector": [600.0, 600.0], "text": "New target chunk 6"},
            {"vector": [700.0, 700.0], "text": "New target chunk 7"},
        ]
    }
    modified_records = dicts_to_indexable_docs(modified_doc_data, tmp_path)

    # Mock the delete_nodes_by_document_id method to verify it gets called
    delete_called = []
    original_delete = adapter.delete_nodes_by_document_id

    async def mock_delete(document_id: str):
        delete_called.append(document_id)
        return await original_delete(document_id)

    adapter.delete_nodes_by_document_id = mock_delete

    # Add modified chunks - this should trigger deletion of old target_doc chunks only
    await adapter.add_chunks_with_embeddings(modified_records)

    # Verify delete was called for the target document only
    assert "target_doc" in delete_called
    assert "other_doc" not in delete_called

    # Verify final count: 7 new target chunks + 3 other chunks = 10 total
    final_count = await adapter.count_records()
    assert final_count == 10

    # Verify the target document now has the new chunks
    new_target_results = await adapter.search(
        VectorStoreQuery(query_string="New target")
    )
    assert len(new_target_results) == 7
    assert all("New target" in result.chunk_text for result in new_target_results)

    # Verify old target chunks are completely gone
    try:
        old_target_results = await adapter.search(
            VectorStoreQuery(query_string="Original")
        )
        # Should find no results since "Original" was only in the old chunks
        assert len(old_target_results) == 0
    except Warning as w:
        # This is expected - LanceDB raises a Warning for empty results
        assert "query results are empty" in str(w)

    # Verify other document is completely unaffected
    final_other_results = await adapter.search(VectorStoreQuery(query_string="Other"))
    assert len(final_other_results) == 3
    assert all("Other doc" in result.chunk_text for result in final_other_results)

    # Verify all other document chunks still have the same content
    other_texts = [result.chunk_text for result in final_other_results]
    expected_other_texts = [
        "Other doc chunk 1",
        "Other doc chunk 2",
        "Other doc chunk 3",
    ]
    for expected_text in expected_other_texts:
        assert any(expected_text in text for text in other_texts)


@pytest.mark.asyncio
async def test_delete_nodes_by_document_id_direct(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Test delete_nodes_by_document_id method directly."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Create two documents with multiple chunks each
    doc1_data = {
        "document_1": [
            {"vector": [1.0, 1.0], "text": "Alpha content part 1"},
            {"vector": [2.0, 2.0], "text": "Alpha content part 2"},
            {"vector": [3.0, 3.0], "text": "Alpha content part 3"},
        ]
    }
    doc1_records = dicts_to_indexable_docs(doc1_data, tmp_path)

    doc2_data = {
        "document_2": [
            {"vector": [10.0, 10.0], "text": "Beta content section 1"},
            {"vector": [20.0, 20.0], "text": "Beta content section 2"},
        ]
    }
    doc2_records = dicts_to_indexable_docs(doc2_data, tmp_path)

    # Add both documents
    await adapter.add_chunks_with_embeddings(doc1_records)
    await adapter.add_chunks_with_embeddings(doc2_records)

    # Verify both documents are in the database (3 + 2 = 5 chunks)
    initial_count = await adapter.count_records()
    assert initial_count == 5

    # Verify we can find chunks from both documents
    doc1_results = await adapter.search(VectorStoreQuery(query_string="Alpha"))
    assert len(doc1_results) == 3

    doc2_results = await adapter.search(VectorStoreQuery(query_string="Beta"))
    assert len(doc2_results) == 2

    # Test deleting document_1 chunks using delete_nodes_by_document_id
    await adapter.delete_nodes_by_document_id("document_1")

    # Verify document_1 chunks are gone
    count_after_delete = await adapter.count_records()
    assert count_after_delete == 2  # Only document_2 chunks remain

    # Verify document_1 chunks are no longer searchable
    try:
        doc1_results_after = await adapter.search(
            VectorStoreQuery(query_string="Alpha")
        )
        assert len(doc1_results_after) == 0
    except Warning as w:
        # LanceDB raises a Warning for empty results
        assert "query results are empty" in str(w)

    # Verify document_2 chunks are still there and unaffected
    doc2_results_after = await adapter.search(VectorStoreQuery(query_string="Beta"))
    assert len(doc2_results_after) == 2
    assert all("Beta" in result.chunk_text for result in doc2_results_after)

    # Test deleting the remaining document
    await adapter.delete_nodes_by_document_id("document_2")

    # Verify all chunks are gone
    final_count = await adapter.count_records()
    assert final_count == 0

    # Test deleting from non-existent document (should not error)
    await adapter.delete_nodes_by_document_id("non_existent_document")

    # Count should still be 0
    count_after_non_existent = await adapter.count_records()
    assert count_after_non_existent == 0


@pytest.mark.asyncio
async def test_delete_nodes_by_document_id_empty_table(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
):
    """Test delete_nodes_by_document_id on empty/non-existent table."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Test deleting from empty table (should not error due to TableNotFoundError handling)
    await adapter.delete_nodes_by_document_id("some_document_id")

    # Verify count is still 0
    count = await adapter.count_records()
    assert count == 0


def generate_benchmark_data(
    doc_count: int,
    chunks_per_doc: int,
    vector_size: int,
    word_count: int,
    tmp_path: Path,
) -> list[DocumentWithChunksAndEmbeddings]:
    """Generate random data for benchmarking."""

    def generate_word_pool(target_size: int) -> list[str]:
        """Generate a pool of random words using common prefixes, roots, and suffixes."""
        prefixes = [
            "pre",
            "un",
            "re",
            "in",
            "dis",
            "en",
            "non",
            "over",
            "mis",
            "sub",
            "inter",
            "super",
            "anti",
            "semi",
            "multi",
            "auto",
            "co",
            "de",
            "ex",
            "pro",
        ]
        roots = [
            "act",
            "form",
            "port",
            "dict",
            "ject",
            "rupt",
            "scrib",
            "struct",
            "tract",
            "vert",
            "vis",
            "spect",
            "mit",
            "duc",
            "fac",
            "cap",
            "cred",
            "grad",
            "loc",
            "mov",
            "ped",
            "pend",
            "pos",
            "sect",
            "sent",
            "serv",
            "sign",
            "sist",
            "spec",
            "tain",
            "temp",
            "tend",
            "terr",
            "test",
            "text",
            "tort",
            "typ",
            "urb",
            "vac",
            "val",
            "ven",
            "vers",
            "vid",
            "voc",
            "volv",
        ]
        suffixes = [
            "tion",
            "sion",
            "ness",
            "ment",
            "able",
            "ible",
            "ful",
            "less",
            "ing",
            "ed",
            "er",
            "est",
            "ly",
            "ity",
            "ous",
            "ive",
            "al",
            "ic",
            "ical",
            "ary",
            "ory",
            "ure",
            "ade",
            "age",
            "ance",
            "ence",
            "dom",
            "hood",
            "ship",
            "ward",
            "wise",
            "like",
            "some",
            "teen",
            "ty",
            "th",
            "ish",
            "esque",
        ]

        words = set()

        # Generate combinations
        while len(words) < target_size:
            # Simple root words
            if random.random() < 0.3:
                words.add(random.choice(roots))
            # Prefix + root
            elif random.random() < 0.6:
                words.add(random.choice(prefixes) + random.choice(roots))
            # Root + suffix
            elif random.random() < 0.8:
                words.add(random.choice(roots) + random.choice(suffixes))
            # Prefix + root + suffix
            else:
                words.add(
                    random.choice(prefixes)
                    + random.choice(roots)
                    + random.choice(suffixes)
                )

        return list(words)

    # Generate word pool that's ~25x the word_count for variety
    target_pool_size = max(
        word_count * 25, 100
    )  # At least 100 words, scale dictionary with word_count*25
    words = generate_word_pool(target_pool_size)

    results = []
    for i in range(doc_count):
        doc_id = f"doc_{i:05d}"

        # Generate random text (word_count words) - allow repetition for variety
        selected_words = random.choices(words, k=word_count)
        text_content = " ".join(selected_words)

        # Generate random vector_size-dimensional vector
        vector = [random.uniform(-1.0, 1.0) for _ in range(vector_size)]

        # Create chunked document with single chunk
        chunked_document = ChunkedDocument(
            chunker_config_id="test_chunker",
            chunks=[
                Chunk(content=KilnAttachmentModel.from_data(text_content, "text/plain"))
                for _ in range(chunks_per_doc)
            ],
            path=tmp_path / f"chunked_document_{i}.kiln",
        )

        # Create chunk embeddings
        chunk_embeddings = ChunkEmbeddings(
            embedding_config_id="test_embedding",
            embeddings=[Embedding(vector=vector) for _ in range(chunks_per_doc)],
            path=tmp_path / f"chunk_embeddings_{i}.kiln",
        )

        results.append(
            DocumentWithChunksAndEmbeddings(
                document_id=doc_id,
                chunked_document=chunked_document,
                chunk_embeddings=chunk_embeddings,
            )
        )

    return results


@pytest.mark.benchmark
# Not actually paid, but we want the "must be run manually" feature of the paid marker as this is very slow
@pytest.mark.paid
def test_benchmark_add_chunks(
    benchmark,
    hybrid_vector_store_config,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Benchmark adding chunks with embeddings to LanceDB."""

    doc_count = 1000
    chunks_per_doc = 50
    vector_size = 1024
    word_count = 200

    # Set random seed for reproducible results
    random.seed(42)

    # Generate random data items (this is not benchmarked)
    benchmark_data = generate_benchmark_data(
        doc_count, chunks_per_doc, vector_size, word_count, tmp_path
    )

    # Create RAG config and adapter (not benchmarked)
    rag_config = create_rag_config_factory(hybrid_vector_store_config, embedding_config)
    adapter = asyncio.run(
        vector_store_adapter_for_config(rag_config, hybrid_vector_store_config)
    )

    # Benchmark only the index loading
    def add_chunks():
        return asyncio.run(adapter.add_chunks_with_embeddings(benchmark_data))

    # one iteration
    benchmark.pedantic(add_chunks, rounds=1, iterations=1)
    stats = benchmark.stats.stats

    # Verify that data was actually added
    async def verify_count():
        final_count = await adapter.count_records()
        return final_count

    final_count = asyncio.run(verify_count())
    assert final_count == doc_count * chunks_per_doc, (
        f"Expected {doc_count} records, got {final_count}"
    )

    # Expect min 2500 ops per second
    max_time = (doc_count * chunks_per_doc) / 2500
    if stats.max > max_time:
        pytest.fail(
            f"Average time per iteration: {stats.mean:.4f}s, expected less than {max_time:.4f}s"
        )


@pytest.mark.asyncio
async def test_delete_nodes_not_in_set_basic_functionality(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test basic functionality of delete_nodes_not_in_set - keep some docs, delete others."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Add both documents (doc_001 and doc_002)
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Verify both documents are there (4 chunks each = 8 total)
    initial_count = await adapter.count_records()
    assert initial_count == 8

    # Keep only doc_001, delete doc_002
    keep_set = {"doc_001"}
    await adapter.delete_nodes_not_in_set(keep_set)

    # Verify only doc_001 chunks remain
    final_count = await adapter.count_records()
    assert final_count == 4

    # Verify doc_001 chunks are still searchable
    doc1_results = await adapter.search(VectorStoreQuery(query_string="population"))
    assert len(doc1_results) > 0
    assert all("doc_001" == result.document_id for result in doc1_results)

    # Verify doc_002 chunks are gone
    doc2_results = await adapter.search(VectorStoreQuery(query_string="area"))
    assert len(doc2_results) == 0


@pytest.mark.asyncio
async def test_delete_nodes_not_in_set_empty_set(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test delete_nodes_not_in_set with empty set - should delete all nodes."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Add both documents
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Verify documents are there
    initial_count = await adapter.count_records()
    assert initial_count == 8

    # Delete all nodes (empty keep set)
    empty_set = set()
    await adapter.delete_nodes_not_in_set(empty_set)

    # Verify all nodes are deleted
    final_count = await adapter.count_records()
    assert final_count == 0


@pytest.mark.asyncio
async def test_delete_nodes_not_in_set_complete_set(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test delete_nodes_not_in_set with complete set - should delete no nodes."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Add both documents
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Verify documents are there
    initial_count = await adapter.count_records()
    assert initial_count == 8

    # Keep all documents
    complete_set = {"doc_001", "doc_002"}
    await adapter.delete_nodes_not_in_set(complete_set)

    # Verify no nodes are deleted
    final_count = await adapter.count_records()
    assert final_count == 8

    # Verify both documents are still searchable
    doc1_results = await adapter.search(VectorStoreQuery(query_string="population"))
    assert len(doc1_results) > 0

    doc2_results = await adapter.search(VectorStoreQuery(query_string="area"))
    assert len(doc2_results) > 0


@pytest.mark.asyncio
async def test_delete_nodes_not_in_set_partial_set(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
    tmp_path,
):
    """Test delete_nodes_not_in_set with partial set - keep some, delete others."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Create three documents for more complex testing
    three_docs_data = {
        "keep_doc_1": [{"vector": [1.0, 1.0], "text": "Keep document one content"}],
        "delete_doc_2": [{"vector": [2.0, 2.0], "text": "Delete document two content"}],
        "keep_doc_3": [{"vector": [3.0, 3.0], "text": "Keep document three content"}],
    }
    three_docs = dicts_to_indexable_docs(three_docs_data, tmp_path)

    # Add all three documents
    await adapter.add_chunks_with_embeddings(three_docs)

    # Verify all documents are there
    initial_count = await adapter.count_records()
    assert initial_count == 3

    # Keep documents 1 and 3, delete document 2
    keep_set = {"keep_doc_1", "keep_doc_3"}
    await adapter.delete_nodes_not_in_set(keep_set)

    # Verify only 2 documents remain
    final_count = await adapter.count_records()
    assert final_count == 2

    # Verify kept documents are still searchable using more specific terms
    keep1_results = await adapter.search(VectorStoreQuery(query_string="one"))
    assert len(keep1_results) == 1
    assert keep1_results[0].document_id == "keep_doc_1"

    keep3_results = await adapter.search(VectorStoreQuery(query_string="three"))
    assert len(keep3_results) == 1
    assert keep3_results[0].document_id == "keep_doc_3"

    # Verify deleted document is gone
    delete_results = await adapter.search(VectorStoreQuery(query_string="two"))
    assert len(delete_results) == 0


@pytest.mark.asyncio
async def test_delete_nodes_not_in_set_uninitialized_table(
    fts_vector_store_config,
    embedding_config,
    create_rag_config_factory,
):
    """Test delete_nodes_not_in_set with uninitialized table - should raise TableNotFoundError."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Don't add any data, so table remains uninitialized
    # The table property will raise TableNotFoundError when accessed
    with pytest.raises(TableNotFoundError, match="Table vectors is not initialized"):
        await adapter.delete_nodes_not_in_set({"doc_001"})


@pytest.mark.asyncio
async def test_delete_nodes_not_in_set_empty_table(
    fts_vector_store_config,
    mock_chunked_documents,
    embedding_config,
    create_rag_config_factory,
):
    """Test delete_nodes_not_in_set with empty table - should handle gracefully."""
    rag_config = create_rag_config_factory(fts_vector_store_config, embedding_config)
    adapter = LanceDBAdapter(rag_config, fts_vector_store_config)

    # Create table by adding data, then delete all to make it empty
    await adapter.add_chunks_with_embeddings(mock_chunked_documents)

    # Delete all documents to make table empty but initialized
    await adapter.delete_nodes_not_in_set(set())  # Empty set deletes everything

    # Verify table is empty
    initial_count = await adapter.count_records()
    assert initial_count == 0

    # Try to delete from empty table - should not error
    await adapter.delete_nodes_not_in_set({"doc_001"})

    # Verify count is still 0
    final_count = await adapter.count_records()
    assert final_count == 0
