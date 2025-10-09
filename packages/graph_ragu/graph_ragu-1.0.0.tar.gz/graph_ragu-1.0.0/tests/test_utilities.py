"""
Test utilities and helper functions for RAGU testing.

This module provides common testing utilities, mock objects, and helper functions
that can be reused across different test modules.
"""

import pandas as pd
import networkx as nx
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, MagicMock

from ragu.common.llm import BaseLLM
from ragu.graph.types import Entity, Relation, Community


class MockLLMClient(BaseLLM):
    """
    Mock LLM client for testing that can be configured with different responses.
    """
    
    def __init__(self):
        super().__init__()
        self.responses = []
        self.call_count = 0
    
    def set_responses(self, responses: List[Dict[str, Any]]):
        """
        Set mock responses for batch processing.
        
        Args:
            responses: List of response dictionaries to return
        """
        self.responses = responses
        self.call_count = 0
    
    def batch_forward(self, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mock batch forward method that returns configured responses.
        
        Args:
            inputs: List of input dictionaries
            
        Returns:
            List of response dictionaries
        """
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return [response] * len(inputs)
        return []
    
    def reset(self):
        """Reset the mock client state."""
        self.responses = []
        self.call_count = 0


class TestDataFactory:
    """
    Factory class for creating test data objects.
    """
    
    @staticmethod
    def create_sample_entities_df() -> pd.DataFrame:
        """Create a sample entities DataFrame for testing."""
        return pd.DataFrame({
            "entity_name": ["John", "Microsoft", "Alice", "Google"],
            "entity_type": ["Person", "Organization", "Person", "Organization"],
            "description": [
                "Software engineer at Microsoft",
                "Technology company based in Seattle",
                "Data scientist at Google",
                "Technology company based in Mountain View"
            ],
            "chunk_id": [["chunk_1"], ["chunk_1"], ["chunk_2"], ["chunk_2"]]
        })
    
    @staticmethod
    def create_sample_relations_df() -> pd.DataFrame:
        """Create a sample relations DataFrame for testing."""
        return pd.DataFrame({
            "source_entity": ["John", "Microsoft", "Alice", "Google"],
            "target_entity": ["Microsoft", "Seattle", "Google", "Mountain View"],
            "relationship_description": ["works at", "based in", "works at", "based in"],
            "relationship_strength": [0.9, 0.8, 0.9, 0.8],
            "chunk_id": [["chunk_1"], ["chunk_1"], ["chunk_2"], ["chunk_2"]]
        })
    
    @staticmethod
    def create_sample_chunks_df() -> pd.DataFrame:
        """Create a sample chunks DataFrame for testing."""
        return pd.DataFrame({
            "chunk": [
                "John is a software engineer at Microsoft. Microsoft is based in Seattle.",
                "Alice is a data scientist at Google. Google is based in Mountain View."
            ],
            "chunk_id": ["chunk_1", "chunk_2"]
        })
    
    @staticmethod
    def create_sample_entities() -> List[Entity]:
        """Create a list of sample Entity objects for testing."""
        return [
            Entity(
                id=1,
                entity_name="John",
                entity_type="Person",
                description="Software engineer",
                source_chunk_id=["chunk_1"],
                clusters_id=[]
            ),
            Entity(
                id=2,
                entity_name="Microsoft",
                entity_type="Organization",
                description="Technology company",
                source_chunk_id=["chunk_1"],
                clusters_id=[]
            ),
            Entity(
                id=3,
                entity_name="Alice",
                entity_type="Person",
                description="Data scientist",
                source_chunk_id=["chunk_2"],
                clusters_id=[]
            )
        ]
    
    @staticmethod
    def create_sample_relations() -> List[Relation]:
        """Create a list of sample Relation objects for testing."""
        entities = TestDataFactory.create_sample_entities()
        return [
            Relation(
                source_entity=entities[0],  # John
                target_entity=entities[1],  # Microsoft
                description="works at",
                relation_strength=0.9
            ),
            Relation(
                source_entity=entities[2],  # Alice
                target_entity=entities[1],  # Microsoft
                description="works at",
                relation_strength=0.8
            )
        ]
    
    @staticmethod
    def create_sample_communities() -> List[Community]:
        """Create a list of sample Community objects for testing."""
        return [
            Community(
                level=0,
                cluster_id=1,
                entities=[("John", "Software engineer"), ("Microsoft", "Technology company")],
                relations=[("John", "Microsoft", "works at")]
            ),
            Community(
                level=0,
                cluster_id=2,
                entities=[("Alice", "Data scientist"), ("Google", "Technology company")],
                relations=[("Alice", "Google", "works at")]
            )
        ]
    
    @staticmethod
    def create_sample_graph() -> nx.Graph:
        """Create a sample NetworkX graph for testing."""
        graph = nx.Graph()
        
        # Add nodes
        graph.add_node("John", entity_type="Person", description="Software engineer")
        graph.add_node("Microsoft", entity_type="Organization", description="Technology company")
        graph.add_node("Alice", entity_type="Person", description="Data scientist")
        
        # Add edges
        graph.add_edge("John", "Microsoft", description="works at", weight=0.9)
        graph.add_edge("Alice", "Microsoft", description="works at", weight=0.8)
        
        return graph


class MockChunker:
    """
    Mock chunker for testing.
    """
    
    def __init__(self, chunks_df: Optional[pd.DataFrame] = None):
        self.chunks_df = chunks_df or TestDataFactory.create_sample_chunks_df()
    
    def __call__(self, documents: List[str]) -> pd.DataFrame:
        """Mock chunker call method."""
        return self.chunks_df
    
    def split(self, documents: List[str]) -> pd.DataFrame:
        """Mock chunker split method."""
        return self.chunks_df


class MockTripletExtractor:
    """
    Mock triplet extractor for testing.
    """
    
    def __init__(self, entities_df: Optional[pd.DataFrame] = None, 
                 relations_df: Optional[pd.DataFrame] = None):
        self.entities_df = entities_df or TestDataFactory.create_sample_entities_df()
        self.relations_df = relations_df or TestDataFactory.create_sample_relations_df()
    
    def __call__(self, chunks_df: pd.DataFrame, **kwargs) -> tuple:
        """Mock triplet extractor call method."""
        return self.entities_df, self.relations_df
    
    def extract_entities_and_relationships(self, chunks_df: pd.DataFrame, **kwargs) -> tuple:
        """Mock triplet extractor extract method."""
        return self.entities_df, self.relations_df


class TestAssertions:
    """
    Custom assertion methods for testing.
    """
    
    @staticmethod
    def assert_dataframe_structure(df: pd.DataFrame, expected_columns: List[str]):
        """
        Assert that a DataFrame has the expected structure.
        
        Args:
            df: DataFrame to check
            expected_columns: List of expected column names
        """
        assert isinstance(df, pd.DataFrame), "Result should be a DataFrame"
        assert all(col in df.columns for col in expected_columns), \
            f"DataFrame should contain columns: {expected_columns}"
    
    @staticmethod
    def assert_entity_structure(entity: Entity):
        """
        Assert that an Entity object has the expected structure.
        
        Args:
            entity: Entity object to check
        """
        assert isinstance(entity, Entity), "Should be an Entity object"
        assert hasattr(entity, 'entity_name'), "Entity should have entity_name"
        assert hasattr(entity, 'entity_type'), "Entity should have entity_type"
        assert hasattr(entity, 'description'), "Entity should have description"
        assert hasattr(entity, 'source_chunk_id'), "Entity should have source_chunk_id"
    
    @staticmethod
    def assert_relation_structure(relation: Relation):
        """
        Assert that a Relation object has the expected structure.
        
        Args:
            relation: Relation object to check
        """
        assert isinstance(relation, Relation), "Should be a Relation object"
        assert hasattr(relation, 'source_entity'), "Relation should have source_entity"
        assert hasattr(relation, 'target_entity'), "Relation should have target_entity"
        assert hasattr(relation, 'description'), "Relation should have description"
        assert hasattr(relation, 'relation_strength'), "Relation should have relation_strength"
    
    @staticmethod
    def assert_community_structure(community: Community):
        """
        Assert that a Community object has the expected structure.
        
        Args:
            community: Community object to check
        """
        assert isinstance(community, Community), "Should be a Community object"
        assert hasattr(community, 'level'), "Community should have level"
        assert hasattr(community, 'cluster_id'), "Community should have cluster_id"
        assert hasattr(community, 'entities'), "Community should have entities"
        assert hasattr(community, 'relations'), "Community should have relations"
    
    @staticmethod
    def assert_graph_structure(graph: nx.Graph, expected_nodes: int = None, 
                              expected_edges: int = None):
        """
        Assert that a NetworkX graph has the expected structure.
        
        Args:
            graph: NetworkX graph to check
            expected_nodes: Expected number of nodes (optional)
            expected_edges: Expected number of edges (optional)
        """
        assert isinstance(graph, nx.Graph), "Should be a NetworkX Graph"
        if expected_nodes is not None:
            assert graph.number_of_nodes() == expected_nodes, \
                f"Graph should have {expected_nodes} nodes"
        if expected_edges is not None:
            assert graph.number_of_edges() == expected_edges, \
                f"Graph should have {expected_edges} edges"


def create_mock_prompt_tool(responses: List[Dict[str, Any]]):
    """
    Create a mock prompt tool with configured responses.
    
    Args:
        responses: List of response dictionaries
        
    Returns:
        Mock prompt tool object
    """
    mock_tool = Mock()
    mock_tool.batch_forward = Mock(side_effect=lambda client, inputs: responses[:len(inputs)])
    return mock_tool


def create_mock_batch_generator(batches: List[List]):
    """
    Create a mock batch generator with configured batches.
    
    Args:
        batches: List of batches to return
        
    Returns:
        Mock batch generator object
    """
    mock_generator = Mock()
    mock_generator.get_batches.return_value = batches
    mock_generator.__len__ = Mock(return_value=len(batches))
    return mock_generator


def assert_chunk_id_uniqueness(chunks_df: pd.DataFrame):
    """
    Assert that chunk IDs in a DataFrame are unique.
    
    Args:
        chunks_df: DataFrame with chunk_id column
    """
    chunk_ids = chunks_df["chunk_id"].tolist()
    assert len(chunk_ids) == len(set(chunk_ids)), "Chunk IDs should be unique"


def assert_entity_normalization(entities_df: pd.DataFrame):
    """
    Assert that entity names are properly normalized (uppercase, Ё->Е).
    
    Args:
        entities_df: DataFrame with entity_name column
    """
    for entity_name in entities_df["entity_name"]:
        assert entity_name.isupper(), f"Entity name should be uppercase: {entity_name}"
        assert "Ё" not in entity_name, f"Entity name should not contain Ё: {entity_name}"


def assert_relation_normalization(relations_df: pd.DataFrame):
    """
    Assert that relation entity names are properly normalized.
    
    Args:
        relations_df: DataFrame with source_entity and target_entity columns
    """
    for _, row in relations_df.iterrows():
        assert row["source_entity"].isupper(), "Source entity should be uppercase"
        assert row["target_entity"].isupper(), "Target entity should be uppercase"
        assert "Ё" not in row["source_entity"], "Source entity should not contain Ё"
        assert "Ё" not in row["target_entity"], "Target entity should not contain Ё"