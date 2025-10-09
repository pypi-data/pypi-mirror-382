"""
Tests for Memgraph storage implementations.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from ragu.graph.types import Entity, Relation
from ragu.storage.graph_storage_adapters.memgraph_adapter import MemgraphGraphStorage
from ragu.storage.vdb_storage_adapters.memgraph_vector import MemgraphVectorStorage
from ragu.storage.memgraph_adatper import MemgraphAdapter


class MockEmbedder:
    """Mock embedder for testing."""
    
    def __init__(self, dim: int = 384):
        self.dim = dim
    
    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        # Generate deterministic embeddings for testing
        np.random.seed(42)
        return np.random.rand(len(texts), self.dim).astype(np.float32)


class TestMemgraphGraphStorage(unittest.TestCase):
    """Test cases for MemgraphGraphStorage."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock mgclient to avoid requiring actual Memgraph connection
        self.mgclient_patcher = patch('ragu.storage.graph_storage_adapters.memgraph_adapter.mgclient')
        self.mock_mgclient = self.mgclient_patcher.start()
        
        # Mock connection and cursor
        self.mock_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_mgclient.connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        
        # Initialize storage
        self.storage = MemgraphGraphStorage(
            host="localhost",
            port=7687,
            namespace="test"
        )
        
        # Create test entities
        self.entity1 = Entity(
            id=1,
            entity_name="John Smith",
            entity_type="Person",
            description="Software engineer",
            source_chunk_id=["chunk1"],
            documents_id=["doc1"],
            clusters_id=[]
        )
        
        self.entity2 = Entity(
            id=2,
            entity_name="Jane Doe",
            entity_type="Person",
            description="Data scientist",
            source_chunk_id=["chunk2"],
            documents_id=["doc2"],
            clusters_id=[]
        )
        
        self.relation1 = Relation(
            source_entity=self.entity1,
            target_entity=self.entity2,
            description="works with",
            relation_strength=0.8
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.mgclient_patcher.stop()
    
    def test_initialization(self):
        """Test storage initialization."""
        self.assertEqual(self.storage.host, "localhost")
        self.assertEqual(self.storage.port, 7687)
        self.assertEqual(self.storage.namespace, "test")
        self.assertIsNotNone(self.storage._connection)
        self.assertIsNotNone(self.storage._cursor)
    
    def test_entity_to_properties(self):
        """Test entity to properties conversion."""
        properties = self.storage._entity_to_properties(self.entity1)
        
        self.assertEqual(properties["entity_name"], "John Smith")
        self.assertEqual(properties["entity_type"], "Person")
        self.assertEqual(properties["description"], "Software engineer")
        self.assertEqual(properties["namespace"], "test")
        self.assertIn("created_at", properties)
    
    def test_properties_to_entity(self):
        """Test properties to entity conversion."""
        properties = {
            "entity_name": "Test Entity",
            "entity_type": "Test",
            "description": "Test description",
            "source_chunk_id": '["chunk1"]',
            "documents_id": '["doc1"]',
            "clusters": '[]'
        }
        
        entity = self.storage._properties_to_entity(1, properties)
        
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.entity_name, "Test Entity")
        self.assertEqual(entity.entity_type, "Test")
        self.assertEqual(entity.description, "Test description")
        self.assertEqual(entity.source_chunk_id, ["chunk1"])
        self.assertEqual(entity.documents_id, ["doc1"])
        self.assertEqual(entity.clusters_id, [])
    
    def test_has_node(self):
        """Test node existence check."""
        # Mock query result
        self.mock_cursor.fetchall.return_value = [("node_data",)]
        
        result = asyncio.run(self.storage.has_node(1))
        
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_once()
    
    def test_has_edge(self):
        """Test edge existence check."""
        # Mock query result
        self.mock_cursor.fetchall.return_value = [("edge_data",)]
        
        result = asyncio.run(self.storage.has_edge(1, 2))
        
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_once()
    
    def test_node_degree(self):
        """Test node degree calculation."""
        # Mock query result
        self.mock_cursor.fetchall.return_value = [(5,)]
        
        result = asyncio.run(self.storage.node_degree(1))
        
        self.assertEqual(result, 5)
        self.mock_cursor.execute.assert_called_once()
    
    def test_upsert_entity(self):
        """Test entity upsert."""
        # Mock successful execution
        self.mock_cursor.fetchall.return_value = []
        
        asyncio.run(self.storage.upsert_entity(self.entity1))
        
        self.mock_cursor.execute.assert_called_once()
        call_args = self.mock_cursor.execute.call_args
        self.assertIn("MERGE", call_args[0][0])
        self.assertIn("Entity", call_args[0][0])
    
    def test_upsert_relation(self):
        """Test relation upsert."""
        # Mock successful execution
        self.mock_cursor.fetchall.return_value = []
        
        asyncio.run(self.storage.upsert_relation(self.relation1))
        
        # Should call execute twice (once for each entity, once for relation)
        self.assertEqual(self.mock_cursor.execute.call_count, 3)
    
    def test_clustering(self):
        """Test clustering functionality."""
        # Mock query result
        self.mock_cursor.fetchall.return_value = [
            ("node1", 0),
            ("node2", 1),
            ("node3", 0)
        ]
        
        result = asyncio.run(self.storage.clustering("leiden"))
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 3)
    
    def test_community_schema(self):
        """Test community schema generation."""
        # Mock clustering result
        with patch.object(self.storage, 'clustering') as mock_cluster:
            mock_cluster.return_value = {1: 0, 2: 0, 3: 1}
            
            # Mock edge query result
            self.mock_cursor.fetchall.return_value = [
                ("node1", "node2")
            ]
            
            result = asyncio.run(self.storage.community_schema())
            
            self.assertIsInstance(result, dict)
            self.assertIn("0", result)
            self.assertIn("1", result)


class TestMemgraphVectorStorage(unittest.TestCase):
    """Test cases for MemgraphVectorStorage."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock mgclient
        self.mgclient_patcher = patch('ragu.storage.vdb_storage_adapters.memgraph_vector.mgclient')
        self.mock_mgclient = self.mgclient_patcher.start()
        
        # Mock connection and cursor
        self.mock_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_mgclient.connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        
        # Initialize embedder and storage
        self.embedder = MockEmbedder(dim=384)
        self.storage = MemgraphVectorStorage(
            embedder=self.embedder,
            host="localhost",
            port=7687,
            similarity_threshold=0.5
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.mgclient_patcher.stop()
    
    def test_initialization(self):
        """Test storage initialization."""
        self.assertEqual(self.storage.host, "localhost")
        self.assertEqual(self.storage.port, 7687)
        self.assertEqual(self.storage.vector_dimension, 384)
        self.assertEqual(self.storage.similarity_threshold, 0.5)
        self.assertIsNotNone(self.storage._connection)
        self.assertIsNotNone(self.storage._cursor)
    
    def test_vector_conversion(self):
        """Test vector conversion methods."""
        # Test numpy array to list
        vector = np.array([1.0, 2.0, 3.0])
        vector_list = self.storage._vector_to_list(vector)
        self.assertEqual(vector_list, [1.0, 2.0, 3.0])
        
        # Test list to numpy array
        vector_array = self.storage._list_to_vector(vector_list)
        np.testing.assert_array_equal(vector_array, vector)
    
    def test_upsert(self):
        """Test document upsert."""
        # Mock successful execution
        self.mock_cursor.fetchall.return_value = []
        
        documents = {
            "doc1": {
                "content": "Test document content",
                "category": "test"
            }
        }
        
        result = asyncio.run(self.storage.upsert(documents))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "doc1")
        self.mock_cursor.execute.assert_called_once()
    
    def test_query(self):
        """Test document query."""
        # Mock query result
        mock_node = Mock()
        mock_node.properties = {
            "id": "doc1",
            "content": "Test content",
            "category": "test"
        }
        
        self.mock_cursor.fetchall.return_value = [
            (mock_node, 0.8)
        ]
        
        result = asyncio.run(self.storage.query("test query", top_k=5))
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "doc1")
        self.assertEqual(result[0]["similarity"], 0.8)
        self.assertEqual(result[0]["distance"], 0.2)
    
    def test_get_by_id(self):
        """Test get document by ID."""
        # Mock query result
        mock_node = Mock()
        mock_node.properties = {
            "id": "doc1",
            "content": "Test content",
            "category": "test"
        }
        
        self.mock_cursor.fetchall.return_value = [(mock_node,)]
        
        result = asyncio.run(self.storage.get_by_id("doc1"))
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "doc1")
        self.assertEqual(result["content"], "Test content")
    
    def test_get_document_count(self):
        """Test get document count."""
        # Mock query result
        self.mock_cursor.fetchall.return_value = [(5,)]
        
        count = asyncio.run(self.storage.get_document_count())
        
        self.assertEqual(count, 5)
    
    def test_delete_by_id(self):
        """Test delete document by ID."""
        # Mock successful execution
        self.mock_cursor.fetchall.return_value = []
        
        result = asyncio.run(self.storage.delete_by_id("doc1"))
        
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_once()
    
    def test_clear_all(self):
        """Test clear all documents."""
        # Mock successful execution
        self.mock_cursor.fetchall.return_value = []
        
        asyncio.run(self.storage.clear_all())
        
        self.mock_cursor.execute.assert_called_once()


class TestMemgraphAdapter(unittest.TestCase):
    """Test cases for combined MemgraphAdapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock mgclient for both storages
        self.mgclient_patcher = patch('ragu.storage.memgraph_adatper.mgclient')
        self.mock_mgclient = self.mgclient_patcher.start()
        
        # Mock connection and cursor
        self.mock_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_mgclient.connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        
        # Initialize embedder and adapter
        self.embedder = MockEmbedder(dim=384)
        self.adapter = MemgraphAdapter(
            host="localhost",
            port=7687,
            namespace="test",
            embedder=self.embedder
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.mgclient_patcher.stop()
    
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertIsNotNone(self.adapter.graph_storage)
        self.assertIsNotNone(self.adapter.vector_storage)
        self.assertEqual(self.adapter.namespace, "test")
    
    def test_graph_operations_delegation(self):
        """Test that graph operations are delegated correctly."""
        # Mock successful execution
        self.mock_cursor.fetchall.return_value = []
        
        # Test has_node delegation
        asyncio.run(self.adapter.has_node("test_node"))
        
        # Test upsert_node delegation
        node_data = {
            "entity_name": "Test Entity",
            "entity_type": "Test",
            "description": "Test description"
        }
        asyncio.run(self.adapter.upsert_node("test_node", node_data))
        
        # Should have called execute multiple times
        self.assertGreater(self.mock_cursor.execute.call_count, 0)
    
    def test_vector_operations_delegation(self):
        """Test that vector operations are delegated correctly."""
        # Mock successful execution
        self.mock_cursor.fetchall.return_value = []
        
        # Test upsert delegation
        documents = {
            "doc1": {
                "content": "Test document",
                "category": "test"
            }
        }
        asyncio.run(self.adapter.upsert(documents))
        
        # Test query delegation
        asyncio.run(self.adapter.query("test query", top_k=5))
        
        # Should have called execute multiple times
        self.assertGreater(self.mock_cursor.execute.call_count, 0)
    
    def test_vector_operations_without_embedder(self):
        """Test vector operations fail when embedder is not provided."""
        adapter_no_embedder = MemgraphAdapter(
            host="localhost",
            port=7687,
            namespace="test"
        )
        
        # Should raise RuntimeError for vector operations
        with self.assertRaises(RuntimeError):
            asyncio.run(adapter_no_embedder.query("test", top_k=5))
        
        with self.assertRaises(RuntimeError):
            asyncio.run(adapter_no_embedder.upsert({"doc1": {"content": "test"}}))
    
    def test_callback_delegation(self):
        """Test that callbacks are delegated correctly."""
        # Mock successful execution
        self.mock_cursor.fetchall.return_value = []
        
        # Test callback methods
        asyncio.run(self.adapter.index_start_callback())
        asyncio.run(self.adapter.index_done_callback())
        asyncio.run(self.adapter.query_done_callback())
        
        # Should have called execute multiple times
        self.assertGreater(self.mock_cursor.execute.call_count, 0)


if __name__ == '__main__':
    unittest.main()