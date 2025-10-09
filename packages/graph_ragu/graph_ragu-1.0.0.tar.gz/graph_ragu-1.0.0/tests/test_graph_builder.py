import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import networkx as nx
import asyncio
from typing import List, Dict, Any

from ragu.graph.graph_builder_pipeline import (
    GraphConstructor, CommunitySummarizer, EntitySummarizer, 
    RelationSummarizer, KnowledgeGraphBuilder
)
from ragu.graph.types import Entity, Relation, Community
from ragu.graph.knowledge_graph import KnowledgeGraph
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


class TestGraphConstructor(unittest.TestCase):
    """Test cases for GraphConstructor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.entity1 = Entity(
            id=1,
            entity_name="John",
            entity_type="Person",
            description="Software engineer",
            source_chunk_id=["chunk_1"],
            clusters_id=[]
        )
        self.entity2 = Entity(
            id=2,
            entity_name="Microsoft",
            entity_type="Organization",
            description="Technology company",
            source_chunk_id=["chunk_1"],
            clusters_id=[]
        )
        self.relation = Relation(
            source_entity=self.entity1,
            target_entity=self.entity2,
            description="works at",
            relation_strength=0.9
        )

    def test_build_graph_empty_relations(self):
        """Test building graph with empty relations list."""
        graph = GraphConstructor.build_graph([])
        
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(graph.number_of_nodes(), 0)
        self.assertEqual(graph.number_of_edges(), 0)

    def test_build_graph_single_relation(self):
        """Test building graph with single relation."""
        relations = [self.relation]
        graph = GraphConstructor.build_graph(relations)
        
        self.assertIsInstance(graph, nx.Graph)
        self.assertEqual(graph.number_of_nodes(), 2)
        self.assertEqual(graph.number_of_edges(), 1)
        
        # Check nodes exist
        self.assertTrue(graph.has_node("John"))
        self.assertTrue(graph.has_node("Microsoft"))
        
        # Check edge exists
        self.assertTrue(graph.has_edge("John", "Microsoft"))
        
        # Check node attributes
        john_data = graph.nodes["John"]
        self.assertEqual(john_data["entity_type"], "Person")
        self.assertEqual(john_data["description"], "Software engineer")
        
        microsoft_data = graph.nodes["Microsoft"]
        self.assertEqual(microsoft_data["entity_type"], "Organization")
        self.assertEqual(microsoft_data["description"], "Technology company")
        
        # Check edge attributes
        edge_data = graph.get_edge_data("John", "Microsoft")
        self.assertEqual(edge_data["description"], "works at")
        self.assertEqual(edge_data["weight"], 0.9)

    def test_build_graph_multiple_relations(self):
        """Test building graph with multiple relations."""
        entity3 = Entity(
            id=3,
            entity_name="Seattle",
            entity_type="Location",
            description="City",
            source_chunk_id=["chunk_2"],
            clusters_id=[]
        )
        
        relation2 = Relation(
            source_entity=self.entity2,
            target_entity=entity3,
            description="based in",
            relation_strength=0.8
        )
        
        relations = [self.relation, relation2]
        graph = GraphConstructor.build_graph(relations)
        
        self.assertEqual(graph.number_of_nodes(), 3)
        self.assertEqual(graph.number_of_edges(), 2)
        
        # Check all nodes exist
        self.assertTrue(graph.has_node("John"))
        self.assertTrue(graph.has_node("Microsoft"))
        self.assertTrue(graph.has_node("Seattle"))
        
        # Check all edges exist
        self.assertTrue(graph.has_edge("John", "Microsoft"))
        self.assertTrue(graph.has_edge("Microsoft", "Seattle"))

    def test_build_graph_duplicate_entities(self):
        """Test building graph with duplicate entities in different relations."""
        entity3 = Entity(
            id=3,
            entity_name="Alice",
            entity_type="Person",
            description="Data scientist",
            source_chunk_id=["chunk_2"],
            clusters_id=[]
        )
        
        relation2 = Relation(
            source_entity=entity3,
            target_entity=self.entity2,
            description="works at",
            relation_strength=0.7
        )
        
        relations = [self.relation, relation2]
        graph = GraphConstructor.build_graph(relations)
        
        # Should have 3 nodes (John, Microsoft, Alice)
        self.assertEqual(graph.number_of_nodes(), 3)
        # Should have 2 edges
        self.assertEqual(graph.number_of_edges(), 2)


class TestCommunitySummarizer(unittest.TestCase):
    """Test cases for CommunitySummarizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.summarizer = CommunitySummarizer()
        self.mock_client = MockLLMClient()
        
        self.community1 = Community(
            level=0,
            cluster_id=1,
            entities=[("John", "Software engineer"), ("Microsoft", "Technology company")],
            relations=[("John", "Microsoft", "works at")]
        )
        
        self.community2 = Community(
            level=0,
            cluster_id=2,
            entities=[("Alice", "Data scientist"), ("Google", "Technology company")],
            relations=[("Alice", "Google", "works at")]
        )

    def test_initialization(self):
        """Test summarizer initialization."""
        self.assertIsNotNone(self.summarizer.prompt_tool)

    @patch('ragu.graph.graph_builder.BatchGenerator')
    def test_get_community_summaries_empty(self, mock_batch_generator):
        """Test getting summaries for empty communities list."""
        mock_batch_generator.return_value.get_batches.return_value = []
        mock_batch_generator.return_value.__len__ = lambda x: 0
        
        result = self.summarizer.get_community_summaries(
            [], self.mock_client, batch_size=2
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @patch('ragu.graph.graph_builder.BatchGenerator')
    def test_get_community_summaries_single_community(self, mock_batch_generator):
        """Test getting summaries for single community."""
        mock_batch_generator.return_value.get_batches.return_value = [[self.community1]]
        mock_batch_generator.return_value.__len__ = lambda x: 1
        
        mock_response = [{"summary": "Technology professionals working at major tech companies"}]
        self.mock_client.set_responses(mock_response)
        self.summarizer.prompt_tool.batch_forward = self.mock_client.batch_forward
        
        result = self.summarizer.get_community_summaries(
            [self.community1], self.mock_client, batch_size=1
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        
        summary = result[0]
        self.assertIn("cluster_id", summary)
        self.assertIn("level", summary)
        self.assertIn("community_report", summary)
        self.assertIn("entities", summary)
        self.assertIn("relations", summary)
        
        self.assertEqual(summary["cluster_id"], 1)
        self.assertEqual(summary["level"], 0)

    @patch('ragu.graph.graph_builder.BatchGenerator')
    def test_get_community_summaries_multiple_communities(self, mock_batch_generator):
        """Test getting summaries for multiple communities."""
        communities = [self.community1, self.community2]
        mock_batch_generator.return_value.get_batches.return_value = [communities]
        mock_batch_generator.return_value.__len__ = lambda x: 1
        
        mock_responses = [
            {"summary": "Tech professionals at Microsoft"},
            {"summary": "Tech professionals at Google"}
        ]
        self.mock_client.set_responses(mock_responses)
        self.summarizer.prompt_tool.batch_forward = self.mock_client.batch_forward
        
        result = self.summarizer.get_community_summaries(
            communities, self.mock_client, batch_size=2
        )
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        
        # Check both summaries have correct structure
        for i, summary in enumerate(result):
            self.assertIn("cluster_id", summary)
            self.assertIn("level", summary)
            self.assertIn("community_report", summary)
            self.assertEqual(summary["cluster_id"], i + 1)

    @patch('ragu.graph.graph_builder.BatchGenerator')
    @patch('ragu.graph.graph_builder.logging')
    def test_get_community_summaries_mismatch_warning(self, mock_logging, mock_batch_generator):
        """Test warning when number of summaries doesn't match communities."""
        communities = [self.community1, self.community2]
        mock_batch_generator.return_value.get_batches.return_value = [communities]
        mock_batch_generator.return_value.__len__ = lambda x: 1
        
        # Return only one response for two communities
        mock_responses = [{"summary": "Only one summary"}]
        self.mock_client.set_responses(mock_responses)
        self.summarizer.prompt_tool.batch_forward = self.mock_client.batch_forward
        
        result = self.summarizer.get_community_summaries(
            communities, self.mock_client, batch_size=2
        )
        
        # Should log a warning
        mock_logging.warning.assert_called_once()


class TestEntitySummarizer(unittest.TestCase):
    """Test cases for EntitySummarizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.summarizer = EntitySummarizer()
        self.mock_client = MockLLMClient()
        
        self.entities_df = pd.DataFrame({
            "entity_name": ["John", "John", "Microsoft", "Alice"],
            "entity_type": ["Person", "Person", "Organization", "Person"],
            "description": ["Software engineer", "Developer", "Technology company", "Data scientist"],
            "chunk_id": [["chunk_1"], ["chunk_2"], ["chunk_1"], ["chunk_3"]]
        })

    def test_initialization(self):
        """Test summarizer initialization."""
        self.assertIsNotNone(self.summarizer.prompt_tool)

    def test_merge_entities(self):
        """Test merging entities by name."""
        merged_df = EntitySummarizer.merge_entities(self.entities_df)
        
        self.assertIsInstance(merged_df, pd.DataFrame)
        self.assertEqual(len(merged_df), 3)  # John, Microsoft, Alice
        
        # Check John has merged descriptions
        john_row = merged_df[merged_df["entity_name"] == "John"].iloc[0]
        self.assertEqual(john_row["description"], "Software engineer Developer")
        self.assertEqual(john_row["description_count"], 2)
        
        # Check Microsoft has single description
        microsoft_row = merged_df[merged_df["entity_name"] == "Microsoft"].iloc[0]
        self.assertEqual(microsoft_row["description"], "Technology company")
        self.assertEqual(microsoft_row["description_count"], 1)

    def test_merge_entities_empty(self):
        """Test merging empty entities DataFrame."""
        empty_df = pd.DataFrame(columns=["entity_name", "entity_type", "description", "chunk_id"])
        merged_df = EntitySummarizer.merge_entities(empty_df)
        
        self.assertIsInstance(merged_df, pd.DataFrame)
        self.assertEqual(len(merged_df), 0)

    def test_extract_summary_without_llm(self):
        """Test extracting summary without LLM summarization."""
        result = self.summarizer.extract_summary(
            self.entities_df, self.mock_client, batch_size=2, summarize_with_llm=False
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)  # Merged entities
        self.assertIn("description_count", result.columns)

    @patch('ragu.graph.graph_builder.BatchGenerator')
    def test_extract_summary_with_llm(self, mock_batch_generator):
        """Test extracting summary with LLM summarization."""
        # Mock batch generator for multi-description entities
        mock_batch_generator.return_value.get_batches.return_value = [
            [{"entity_name": "John", "description": "Software engineer Developer", "description_count": 2}]
        ]
        mock_batch_generator.return_value.__len__ = lambda x: 1
        
        mock_response = [{"description": "Software engineer and developer"}]
        self.mock_client.set_responses(mock_response)
        self.summarizer.prompt_tool.batch_forward = self.mock_client.batch_forward
        
        result = self.summarizer.extract_summary(
            self.entities_df, self.mock_client, batch_size=1, summarize_with_llm=True
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("description_count", result.columns)

    def test_summarize_single_description(self):
        """Test summarization with entities having single descriptions."""
        merged_df = EntitySummarizer.merge_entities(self.entities_df)
        result = self.summarizer.summarize(merged_df, self.mock_client, batch_size=2)
        
        # Should return the same DataFrame since all entities have single descriptions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(merged_df))


class TestRelationSummarizer(unittest.TestCase):
    """Test cases for RelationSummarizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.summarizer = RelationSummarizer()
        self.mock_client = MockLLMClient()
        
        self.relations_df = pd.DataFrame({
            "source_entity": ["John", "John", "Microsoft", "Alice"],
            "target_entity": ["Microsoft", "Microsoft", "Seattle", "Google"],
            "relationship_description": ["works at", "employed by", "based in", "works at"],
            "relationship_strength": [0.9, 0.8, 0.7, 0.9],
            "chunk_id": [["chunk_1"], ["chunk_2"], ["chunk_1"], ["chunk_3"]]
        })

    def test_initialization(self):
        """Test summarizer initialization."""
        self.assertIsNotNone(self.summarizer.prompt_tool)

    def test_merge_relationships(self):
        """Test merging relationships by entity pairs."""
        merged_df = RelationSummarizer.merge_relationships(self.relations_df)
        
        self.assertIsInstance(merged_df, pd.DataFrame)
        self.assertEqual(len(merged_df), 3)  # John-Microsoft, Microsoft-Seattle, Alice-Google
        
        # Check John-Microsoft has merged descriptions
        john_microsoft = merged_df[
            (merged_df["source_entity"] == "John") & 
            (merged_df["target_entity"] == "Microsoft")
        ].iloc[0]
        self.assertEqual(john_microsoft["relationship_description"], "works at employed by")
        self.assertEqual(john_microsoft["description_count"], 2)
        self.assertEqual(john_microsoft["relationship_strength"], 0.85)  # Average of 0.9 and 0.8

    def test_merge_relationships_empty(self):
        """Test merging empty relationships DataFrame."""
        empty_df = pd.DataFrame(columns=[
            "source_entity", "target_entity", "relationship_description", 
            "relationship_strength", "chunk_id"
        ])
        merged_df = RelationSummarizer.merge_relationships(empty_df)
        
        self.assertIsInstance(merged_df, pd.DataFrame)
        self.assertEqual(len(merged_df), 0)

    def test_extract_summary_without_llm(self):
        """Test extracting summary without LLM summarization."""
        result = self.summarizer.extract_summary(
            self.relations_df, self.mock_client, batch_size=2, summarize_with_llm=False
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 3)  # Merged relationships
        self.assertIn("description_count", result.columns)

    @patch('ragu.graph.graph_builder.BatchGenerator')
    def test_extract_summary_with_llm(self, mock_batch_generator):
        """Test extracting summary with LLM summarization."""
        # Mock batch generator for multi-description relationships
        mock_batch_generator.return_value.get_batches.return_value = [
            [{"source_entity": "John", "target_entity": "Microsoft", 
              "relationship_description": "works at employed by", "description_count": 2}]
        ]
        mock_batch_generator.return_value.__len__ = lambda x: 1
        
        mock_response = [{"description": "employment relationship"}]
        self.mock_client.set_responses(mock_response)
        self.summarizer.prompt_tool.batch_forward = self.mock_client.batch_forward
        
        result = self.summarizer.extract_summary(
            self.relations_df, self.mock_client, batch_size=1, summarize_with_llm=True
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn("description_count", result.columns)

    def test_summarize_single_description(self):
        """Test summarization with relationships having single descriptions."""
        merged_df = RelationSummarizer.merge_relationships(self.relations_df)
        # Filter to only single descriptions
        single_desc_df = merged_df[merged_df["description_count"] == 1]
        result = self.summarizer.summarize(single_desc_df, self.mock_client, batch_size=2)
        
        # Should return the same DataFrame since all relationships have single descriptions
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), len(single_desc_df))


class TestKnowledgeGraphBuilder(unittest.TestCase):
    """Test cases for KnowledgeGraphBuilder class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MockLLMClient()
        self.mock_chunker = Mock()
        self.mock_triplet_extractor = Mock()
        
        self.builder = KnowledgeGraphBuilder(
            client=self.mock_client,
            chunker=self.mock_chunker,
            triplet_extractor=self.mock_triplet_extractor,
            batch_size=2,
            save_intermediate_results=False,
            auto_save=False
        )

    def test_initialization(self):
        """Test builder initialization."""
        self.assertEqual(self.builder._client, self.mock_client)
        self.assertEqual(self.builder.chunker, self.mock_chunker)
        self.assertEqual(self.builder.triplet_extractor, self.mock_triplet_extractor)
        self.assertEqual(self.builder.batch_size, 2)
        self.assertFalse(self.builder.save_intermediate_results)
        self.assertFalse(self.builder.auto_save)

    def test_get_nodes(self):
        """Test converting entities DataFrame to Entity objects."""
        entities_df = pd.DataFrame({
            "entity_name": ["John", "Microsoft"],
            "entity_type": ["Person", "Organization"],
            "description": ["Software engineer", "Technology company"],
            "chunk_id": [["chunk_1"], ["chunk_1"]]
        })
        
        nodes = self.builder._get_nodes(entities_df)
        
        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 2)
        
        # Check first node
        node1 = nodes[0]
        self.assertIsInstance(node1, Entity)
        self.assertEqual(node1.entity_name, "John")
        self.assertEqual(node1.entity_type, "Person")
        self.assertEqual(node1.description, "Software engineer")
        self.assertEqual(node1.source_chunk_id, ["chunk_1"])

    def test_get_edges(self):
        """Test converting relations DataFrame to Relation objects."""
        # Create nodes first
        entity1 = Entity(
            id=1, entity_name="John", entity_type="Person",
            description="Software engineer", source_chunk_id=["chunk_1"], clusters_id=[]
        )
        entity2 = Entity(
            id=2, entity_name="Microsoft", entity_type="Organization",
            description="Technology company", source_chunk_id=["chunk_1"], clusters_id=[]
        )
        nodes = [entity1, entity2]
        
        relations_df = pd.DataFrame({
            "source_entity": ["John"],
            "target_entity": ["Microsoft"],
            "relationship_description": ["works at"],
            "relationship_strength": [0.9]
        })
        
        edges = self.builder._get_edges(relations_df, nodes)
        
        self.assertIsInstance(edges, list)
        self.assertEqual(len(edges), 1)
        
        # Check first edge
        edge1 = edges[0]
        self.assertIsInstance(edge1, Relation)
        self.assertEqual(edge1.source_entity, entity1)
        self.assertEqual(edge1.target_entity, entity2)
        self.assertEqual(edge1.description, "works at")
        self.assertEqual(edge1.relation_strength, 0.9)

    def test_get_edges_missing_entities(self):
        """Test handling missing entities in relations."""
        entity1 = Entity(
            id=1, entity_name="John", entity_type="Person",
            description="Software engineer", source_chunk_id=["chunk_1"], clusters_id=[]
        )
        nodes = [entity1]  # Missing Microsoft entity
        
        relations_df = pd.DataFrame({
            "source_entity": ["John", "Alice"],
            "target_entity": ["Microsoft", "Google"],
            "relationship_description": ["works at", "works at"],
            "relationship_strength": [0.9, 0.8]
        })
        
        edges = self.builder._get_edges(relations_df, nodes)
        
        # Should only include relations where both entities exist
        self.assertEqual(len(edges), 0)  # No valid relations

    @patch('ragu.graph.graph_builder.GraphConstructor')
    @patch('ragu.graph.graph_builder.EntitySummarizer')
    @patch('ragu.graph.graph_builder.RelationSummarizer')
    @patch('ragu.graph.graph_builder.CommunitySummarizer')
    @patch('ragu.graph.graph_builder.KnowledgeGraph')
    @patch('ragu.graph.graph_builder.asyncio')
    def test_build_complete_pipeline(self, mock_asyncio, mock_kg_class, 
                                   mock_community_summarizer, mock_relation_summarizer,
                                   mock_entity_summarizer, mock_graph_constructor):
        """Test the complete build pipeline."""
        # Mock chunker response
        chunks_df = pd.DataFrame({
            "chunk": ["John works at Microsoft"],
            "chunk_id": ["chunk_1"]
        })
        self.mock_chunker.return_value = chunks_df
        
        # Mock triplet extractor response
        entities_df = pd.DataFrame({
            "entity_name": ["John", "Microsoft"],
            "entity_type": ["Person", "Organization"],
            "description": ["Software engineer", "Technology company"],
            "chunk_id": [["chunk_1"], ["chunk_1"]]
        })
        relations_df = pd.DataFrame({
            "source_entity": ["John"],
            "target_entity": ["Microsoft"],
            "relationship_description": ["works at"],
            "relationship_strength": [0.9],
            "chunk_id": [["chunk_1"]]
        })
        self.mock_triplet_extractor.return_value = (entities_df, relations_df)
        
        # Mock summarizers
        mock_entity_summarizer.return_value.extract_summary.return_value = entities_df
        mock_relation_summarizer.return_value.extract_summary.return_value = relations_df
        
        # Mock graph construction
        mock_graph = nx.Graph()
        mock_graph.add_node("John")
        mock_graph.add_node("Microsoft")
        mock_graph.add_edge("John", "Microsoft")
        mock_graph_constructor.build_graph.return_value = mock_graph
        
        # Mock knowledge graph
        mock_kg = Mock()
        mock_kg.detect_communities.return_value = []
        mock_kg_class.return_value = mock_kg
        
        # Mock community summarizer
        mock_community_summarizer.return_value.get_community_summaries.return_value = []
        
        # Mock asyncio
        mock_asyncio.make_request.return_value = None
        
        # Test build
        documents = ["John works at Microsoft"]
        result = self.builder.extract_graph(documents)
        
        # Verify calls
        self.mock_chunker.assert_called_once_with(documents)
        self.mock_triplet_extractor.assert_called_once_with(chunks_df, client=self.mock_client)
        mock_graph_constructor.build_graph.assert_called_once()
        mock_kg.detect_communities.assert_called_once()
        
        self.assertEqual(result, mock_kg)

    def test_build_missing_components(self):
        """Test build with missing components."""
        builder = KnowledgeGraphBuilder(
            client=self.mock_client,
            chunker=None,
            triplet_extractor=self.mock_triplet_extractor
        )
        
        with self.assertRaises(ValueError):
            builder.extract_graph(["test document"])

    def test_build_missing_triplet_extractor(self):
        """Test build with missing triplet extractor."""
        builder = KnowledgeGraphBuilder(
            client=self.mock_client,
            chunker=self.mock_chunker,
            triplet_extractor=None
        )
        
        with self.assertRaises(ValueError):
            builder.extract_graph(["test document"])


if __name__ == '__main__':
    unittest.main()
