import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from typing import List, Dict, Any

from ragu.triplet.llm_artifact_extractor import TripletLLM
from ragu.triplet.base_artifact_extractor import TripletExtractor
from ragu.common.llm import BaseLLM


class MockLLMClient(BaseLLM):
    """Mock LLM client for testing."""
    
    def __init__(self):
        super().__init__()
        self.responses = []
    
    def set_responses(self, responses: List[Dict[str, Any]]):
        """Set mock responses for batch processing."""
        self.responses = responses
    
    def batch_forward(self, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mock batch forward method."""
        return self.responses[:len(inputs)]


class TestTripletLLM(unittest.TestCase):
    """Test cases for TripletLLM class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = TripletLLM(batch_size=2, validate=False)
        self.mock_client = MockLLMClient()
        
        # Sample chunks data
        self.sample_chunks = pd.DataFrame({
            "chunk": [
                "John works at Microsoft. He is a software engineer.",
                "Microsoft is a technology company based in Seattle.",
                "Alice is a data scientist at Google."
            ],
            "chunk_id": ["chunk_1", "chunk_2", "chunk_3"]
        })

    def test_initialization(self):
        """Test extractor initialization."""
        self.assertEqual(self.extractor.batch_size, 2)
        self.assertFalse(self.extractor.validate)
        self.assertIsNotNone(self.extractor.artifact_extractor_prompt_tool)
        self.assertIsNotNone(self.extractor.artifact_validation_prompt_tool)

    def test_initialization_with_validation(self):
        """Test extractor initialization with validation enabled."""
        extractor = TripletLLM(batch_size=4, validate=True)
        self.assertEqual(extractor.batch_size, 4)
        self.assertTrue(extractor.validate)

    def test_entity_columns(self):
        """Test entity column names."""
        expected_columns = ["entity_name", "entity_type", "description", "chunk_id"]
        self.assertEqual(self.extractor.ENTITY_COLUMNS, expected_columns)

    def test_relation_columns(self):
        """Test relation column names."""
        expected_columns = ["source_entity", "target_entity", "relationship_description", 
                           "relationship_strength", "chunk_id"]
        self.assertEqual(self.extractor.RELATION_COLUMNS, expected_columns)

    @patch('ragu.triplet.triplet_makers.BatchGenerator')
    def test_extract_entities_and_relationships_basic(self, mock_batch_generator):
        """Test basic entity and relationship extraction."""
        # Mock batch generator
        mock_batches = [
            [("John works at Microsoft. He is a software engineer.", "chunk_1")],
            [("Microsoft is a technology company based in Seattle.", "chunk_2")]
        ]
        mock_batch_generator.return_value.get_batches.return_value = mock_batches
        
        # Mock prompt tool responses
        mock_responses = [
            {
                "entities": [
                    {"entity_name": "John", "entity_type": "Person", "description": "Software engineer"},
                    {"entity_name": "Microsoft", "entity_type": "Organization", "description": "Technology company"}
                ],
                "relationships": [
                    {"source_entity": "John", "target_entity": "Microsoft", 
                     "relationship_description": "works at", "relationship_strength": 0.9}
                ]
            },
            {
                "entities": [
                    {"entity_name": "Microsoft", "entity_type": "Organization", "description": "Technology company"},
                    {"entity_name": "Seattle", "entity_type": "Location", "description": "City"}
                ],
                "relationships": [
                    {"source_entity": "Microsoft", "target_entity": "Seattle", 
                     "relationship_description": "based in", "relationship_strength": 0.8}
                ]
            }
        ]
        
        self.mock_client.set_responses(mock_responses)
        self.extractor.artifact_extractor_prompt_tool.batch_forward = self.mock_client.batch_forward
        
        # Test extraction
        entities_df, relations_df = self.extractor.extract_entities_and_relationships(
            self.sample_chunks, client=self.mock_client
        )
        
        # Verify entities
        self.assertIsInstance(entities_df, pd.DataFrame)
        self.assertIn("entity_name", entities_df.columns)
        self.assertIn("entity_type", entities_df.columns)
        self.assertIn("description", entities_df.columns)
        self.assertIn("chunk_id", entities_df.columns)
        self.assertGreater(len(entities_df), 0)
        
        # Verify relations
        self.assertIsInstance(relations_df, pd.DataFrame)
        self.assertIn("source_entity", relations_df.columns)
        self.assertIn("target_entity", relations_df.columns)
        self.assertIn("relationship_description", relations_df.columns)
        self.assertIn("relationship_strength", relations_df.columns)
        self.assertIn("chunk_id", relations_df.columns)
        self.assertGreater(len(relations_df), 0)

    @patch('ragu.triplet.triplet_makers.BatchGenerator')
    def test_extract_entities_and_relationships_with_validation(self, mock_batch_generator):
        """Test extraction with validation enabled."""
        extractor = TripletLLM(batch_size=1, validate=True)
        
        # Mock batch generator
        mock_batches = [[("Test text", "chunk_1")]]
        mock_batch_generator.return_value.get_batches.return_value = mock_batches
        
        # Mock responses for extraction and validation
        extraction_responses = [{
            "entities": [{"entity_name": "Test", "entity_type": "Entity", "description": "Test entity"}],
            "relationships": []
        }]
        
        validation_responses = [{
            "entities": [{"entity_name": "Test", "entity_type": "Entity", "description": "Validated entity"}],
            "relationships": []
        }]
        
        # Set up mock client to return different responses for extraction and validation
        call_count = 0
        def mock_batch_forward(inputs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # First call for extraction
                return extraction_responses
            else:  # Second call for validation
                return validation_responses
        
        extractor.artifact_extractor_prompt_tool.batch_forward = mock_batch_forward
        extractor.artifact_validation_prompt_tool.batch_forward = mock_batch_forward
        
        # Test extraction with validation
        entities_df, relations_df = extractor.extract_entities_and_relationships(
            self.sample_chunks.head(1), client=self.mock_client
        )
        
        self.assertIsInstance(entities_df, pd.DataFrame)
        self.assertIsInstance(relations_df, pd.DataFrame)

    def test_process_parsed_batch(self):
        """Test processing of parsed batch data."""
        parsed_batch = [{
            "entities": [
                {"entity_name": "John", "entity_type": "Person", "description": "Software engineer"}
            ],
            "relationships": [
                {"source_entity": "John", "target_entity": "Microsoft", 
                 "relationship_description": "works at", "relationship_strength": 0.9}
            ]
        }]
        chunks_id = ["chunk_1"]
        entities = []
        relations = []
        
        self.extractor._process_parsed_batch(parsed_batch, chunks_id, entities, relations)
        
        self.assertEqual(len(entities), 1)
        self.assertEqual(len(relations), 1)
        
        # Check entity DataFrame
        entity_df = entities[0]
        self.assertIn("entity_name", entity_df.columns)
        self.assertIn("chunk_id", entity_df.columns)
        self.assertEqual(entity_df.iloc[0]["chunk_id"], "chunk_1")
        
        # Check relation DataFrame
        relation_df = relations[0]
        self.assertIn("source_entity", relation_df.columns)
        self.assertIn("chunk_id", relation_df.columns)
        self.assertEqual(relation_df.iloc[0]["chunk_id"], "chunk_1")

    def test_finalize_dataframes_empty(self):
        """Test finalizing DataFrames with empty data."""
        entities_df, relations_df = self.extractor._finalize_dataframes([], [])
        
        self.assertIsInstance(entities_df, pd.DataFrame)
        self.assertIsInstance(relations_df, pd.DataFrame)
        self.assertEqual(len(entities_df), 0)
        self.assertEqual(len(relations_df), 0)
        
        # Check columns exist
        self.assertEqual(list(entities_df.columns), self.extractor.ENTITY_COLUMNS)
        self.assertEqual(list(relations_df.columns), self.extractor.RELATION_COLUMNS)

    def test_finalize_dataframes_with_data(self):
        """Test finalizing DataFrames with actual data."""
        # Create sample DataFrames
        entity_df1 = pd.DataFrame({
            "entity_name": ["John"],
            "entity_type": ["Person"],
            "description": ["Software engineer"]
        })
        entity_df1["chunk_id"] = "chunk_1"
        
        relation_df1 = pd.DataFrame({
            "source_entity": ["John"],
            "target_entity": ["Microsoft"],
            "relationship_description": ["works at"],
            "relationship_strength": [0.9]
        })
        relation_df1["chunk_id"] = "chunk_1"
        
        entities_df, relations_df = self.extractor._finalize_dataframes([entity_df1], [relation_df1])
        
        self.assertIsInstance(entities_df, pd.DataFrame)
        self.assertIsInstance(relations_df, pd.DataFrame)
        self.assertEqual(len(entities_df), 1)
        self.assertEqual(len(relations_df), 1)
        
        # Check Russian normalization
        self.assertEqual(entities_df.iloc[0]["entity_name"], "JOHN")
        self.assertEqual(relations_df.iloc[0]["source_entity"], "JOHN")
        self.assertEqual(relations_df.iloc[0]["target_entity"], "MICROSOFT")

    def test_finalize_dataframes_russian_normalization(self):
        """Test Russian character normalization."""
        entity_df = pd.DataFrame({
            "entity_name": ["Ёлка"],
            "entity_type": ["Object"],
            "description": ["Christmas tree"]
        })
        entity_df["chunk_id"] = "chunk_1"
        
        relation_df = pd.DataFrame({
            "source_entity": ["Ёлка"],
            "target_entity": ["Дом"],
            "relationship_description": ["находится в"],
            "relationship_strength": [0.8]
        })
        relation_df["chunk_id"] = "chunk_1"
        
        entities_df, relations_df = self.extractor._finalize_dataframes([entity_df], [relation_df])
        
        # Check that Ё is replaced with Е
        self.assertEqual(entities_df.iloc[0]["entity_name"], "ЕЛКА")
        self.assertEqual(relations_df.iloc[0]["source_entity"], "ЕЛКА")
        self.assertEqual(relations_df.iloc[0]["target_entity"], "ДОМ")

    def test_call_method(self):
        """Test the __call__ method."""
        with patch.object(self.extractor, 'extract_entities_and_relationships') as mock_extract:
            mock_extract.return_value = (pd.DataFrame(), pd.DataFrame())
            
            result = self.extractor(self.sample_chunks, client=self.mock_client)
            
            mock_extract.assert_called_once_with(self.sample_chunks, client=self.mock_client)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)

    def test_empty_chunks_handling(self):
        """Test handling of empty chunks DataFrame."""
        empty_chunks = pd.DataFrame(columns=["chunk", "chunk_id"])
        
        with patch('ragu.triplet.triplet_makers.BatchGenerator') as mock_batch_generator:
            mock_batch_generator.return_value.get_batches.return_value = []
            
            entities_df, relations_df = self.extractor.extract_entities_and_relationships(
                empty_chunks, client=self.mock_client
            )
            
            self.assertIsInstance(entities_df, pd.DataFrame)
            self.assertIsInstance(relations_df, pd.DataFrame)
            self.assertEqual(len(entities_df), 0)
            self.assertEqual(len(relations_df), 0)

    def test_batch_processing(self):
        """Test that batch processing works correctly."""
        with patch('ragu.triplet.triplet_makers.BatchGenerator') as mock_batch_generator:
            # Create a mock batch generator that returns multiple batches
            mock_batches = [
                [("Text 1", "chunk_1"), ("Text 2", "chunk_2")],
                [("Text 3", "chunk_3")]
            ]
            mock_batch_generator.return_value.get_batches.return_value = mock_batches
            mock_batch_generator.return_value.__len__ = lambda x: 2
            
            # Mock responses for each batch
            responses = [
                {
                    "entities": [{"entity_name": "Entity1", "entity_type": "Type1", "description": "Desc1"}],
                    "relationships": []
                },
                {
                    "entities": [{"entity_name": "Entity2", "entity_type": "Type2", "description": "Desc2"}],
                    "relationships": []
                }
            ]
            
            self.mock_client.set_responses(responses)
            self.extractor.artifact_extractor_prompt_tool.batch_forward = self.mock_client.batch_forward
            
            entities_df, relations_df = self.extractor.extract_entities_and_relationships(
                self.sample_chunks, client=self.mock_client
            )
            
            # Should process all batches
            self.assertIsInstance(entities_df, pd.DataFrame)
            self.assertIsInstance(relations_df, pd.DataFrame)


class TestTripletExtractorBaseClass(unittest.TestCase):
    """Test cases for the base TripletExtractor class."""

    def test_abstract_method(self):
        """Test that TripletExtractor is abstract and cannot be instantiated."""
        with self.assertRaises(TypeError):
            TripletExtractor()

    def test_registry_functionality(self):
        """Test that triplet extractors are properly registered."""
        # Check that our extractor is registered
        self.assertIn("original", TripletExtractor._registry)

    def test_call_method_signature(self):
        """Test that the base class __call__ method has correct signature."""
        # This test ensures the base class method signature is compatible
        class TestExtractor(TripletExtractor):
            def extract_entities_and_relationships(self, chunks_df, *args, **kwargs):
                return pd.DataFrame(), pd.DataFrame()
        
        extractor = TestExtractor()
        result = extractor(pd.DataFrame())
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()