"""
Tests for duplicate detection functionality.
"""

import unittest
from ragu.graph.types import Entity, Relation
from ragu.utils.duplicate_detector import (
    EntityDuplicateDetector,
    RelationDuplicateDetector,
    ArtifactDuplicateDetector,
    DuplicateGroup
)


class TestEntityDuplicateDetector(unittest.TestCase):
    """Test cases for EntityDuplicateDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = EntityDuplicateDetector()
        
        # Create test entities
        self.entity1 = Entity(
            id=1,
            entity_name="John Smith",
            entity_type="Person",
            description="Software engineer at Microsoft",
            source_chunk_id=["chunk1"],
            documents_id=[],
            clusters_id=[]
        )
        
        self.entity2 = Entity(
            id=2,
            entity_name="John Smith",  # Exact duplicate
            entity_type="Person",
            description="Software engineer at Microsoft",
            source_chunk_id=["chunk2"],
            documents_id=[],
            clusters_id=[]
        )
        
        self.entity3 = Entity(
            id=3,
            entity_name="J. Smith",  # Similar name
            entity_type="Person",
            description="Software engineer at Microsoft",
            source_chunk_id=["chunk3"],
            documents_id=[],
            clusters_id=[]
        )
        
        self.entity4 = Entity(
            id=4,
            entity_name="Jane Doe",
            entity_type="Person",
            description="Data scientist",
            source_chunk_id=["chunk4"],
            documents_id=[],
            clusters_id=[]
        )
        
        self.entity5 = Entity(
            id=5,
            entity_name="John Smith",
            entity_type="Organization",  # Different type
            description="Software engineer at Microsoft",
            source_chunk_id=["chunk5"],
            documents_id=[],
            clusters_id=[]
        )
    
    def test_exact_duplicates(self):
        """Test detection of exact duplicates."""
        entities = [self.entity1, self.entity2]
        duplicates = self.detector.find_duplicates(entities)
        
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(duplicates[0].duplicates), 1)
        self.assertEqual(duplicates[0].primary_item.entity_name, "John Smith")
        self.assertEqual(duplicates[0].duplicates[0].entity_name, "John Smith")
        self.assertGreater(duplicates[0].similarity_score, 0.9)
    
    def test_similar_duplicates(self):
        """Test detection of similar duplicates."""
        entities = [self.entity1, self.entity3]
        duplicates = self.detector.find_duplicates(entities)
        
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(duplicates[0].duplicates), 1)
        self.assertGreater(duplicates[0].similarity_score, 0.7)
    
    def test_no_duplicates(self):
        """Test when no duplicates exist."""
        entities = [self.entity1, self.entity4]
        duplicates = self.detector.find_duplicates(entities)
        
        self.assertEqual(len(duplicates), 0)
    
    def test_entity_type_matching(self):
        """Test entity type matching requirement."""
        entities = [self.entity1, self.entity5]
        duplicates = self.detector.find_duplicates(entities)
        
        # Should not find duplicates due to different entity types
        self.assertEqual(len(duplicates), 0)
    
    def test_multiple_duplicates(self):
        """Test detection of multiple duplicate groups."""
        entities = [self.entity1, self.entity2, self.entity3, self.entity4]
        duplicates = self.detector.find_duplicates(entities)
        
        # Should find one group with entity1, entity2, entity3
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(duplicates[0].duplicates), 2)


class TestRelationDuplicateDetector(unittest.TestCase):
    """Test cases for RelationDuplicateDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = RelationDuplicateDetector()
        
        # Create test entities
        self.entity1 = Entity(
            id=1,
            entity_name="John Smith",
            entity_type="Person",
            description="Software engineer",
            source_chunk_id=["chunk1"],
            documents_id=[],
            clusters_id=[]
        )
        
        self.entity2 = Entity(
            id=2,
            entity_name="Jane Doe",
            entity_type="Person",
            description="Data scientist",
            source_chunk_id=["chunk2"],
            documents_id=[],
            clusters_id=[]
        )
        
        # Create test relations
        self.relation1 = Relation(
            source_entity=self.entity1,
            target_entity=self.entity2,
            description="works with",
            relation_strength=0.8
        )
        
        self.relation2 = Relation(
            source_entity=self.entity1,
            target_entity=self.entity2,
            description="works with",  # Exact duplicate
            relation_strength=0.8
        )
        
        self.relation3 = Relation(
            source_entity=self.entity2,
            target_entity=self.entity1,
            description="works with",  # Bidirectional duplicate
            relation_strength=0.8
        )
        
        self.relation4 = Relation(
            source_entity=self.entity1,
            target_entity=self.entity2,
            description="collaborates with",  # Different description
            relation_strength=0.8
        )
        
        self.relation5 = Relation(
            source_entity=self.entity1,
            target_entity=self.entity2,
            description="works with",
            relation_strength=0.9  # Different strength
        )
    
    def test_exact_duplicates(self):
        """Test detection of exact duplicates."""
        relations = [self.relation1, self.relation2]
        duplicates = self.detector.find_duplicates(relations)
        
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(duplicates[0].duplicates), 1)
        self.assertGreater(duplicates[0].similarity_score, 0.9)
    
    def test_bidirectional_duplicates(self):
        """Test detection of bidirectional duplicates."""
        relations = [self.relation1, self.relation3]
        duplicates = self.detector.find_duplicates(relations)
        
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(duplicates[0].duplicates), 1)
    
    def test_different_descriptions(self):
        """Test that different descriptions are not considered duplicates."""
        relations = [self.relation1, self.relation4]
        duplicates = self.detector.find_duplicates(relations)
        
        self.assertEqual(len(duplicates), 0)
    
    def test_different_strengths(self):
        """Test that different strengths are not considered duplicates."""
        relations = [self.relation1, self.relation5]
        duplicates = self.detector.find_duplicates(relations)
        
        self.assertEqual(len(duplicates), 0)


class TestArtifactDuplicateDetector(unittest.TestCase):
    """Test cases for ArtifactDuplicateDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = ArtifactDuplicateDetector()
        
        # Create test entities
        self.entity1 = Entity(
            id=1,
            entity_name="John Smith",
            entity_type="Person",
            description="Software engineer",
            source_chunk_id=["chunk1"],
            documents_id=[],
            clusters_id=[]
        )
        
        self.entity2 = Entity(
            id=2,
            entity_name="John Smith",  # Duplicate
            entity_type="Person",
            description="Software engineer",
            source_chunk_id=["chunk2"],
            documents_id=[],
            clusters_id=[]
        )
        
        self.entity3 = Entity(
            id=3,
            entity_name="Jane Doe",
            entity_type="Person",
            description="Data scientist",
            source_chunk_id=["chunk3"],
            documents_id=[],
            clusters_id=[]
        )
        
        # Create test relations
        self.relation1 = Relation(
            source_entity=self.entity1,
            target_entity=self.entity3,
            description="works with",
            relation_strength=0.8
        )
        
        self.relation2 = Relation(
            source_entity=self.entity2,
            target_entity=self.entity3,
            description="works with",  # Duplicate
            relation_strength=0.8
        )
    
    def test_find_all_duplicates(self):
        """Test finding all duplicates."""
        entities = [self.entity1, self.entity2, self.entity3]
        relations = [self.relation1, self.relation2]
        
        result = self.detector.find_all_duplicates(entities, relations)
        
        self.assertIn('entities', result)
        self.assertIn('relations', result)
        self.assertEqual(len(result['entities']), 1)
        self.assertEqual(len(result['relations']), 1)
    
    def test_get_duplicate_statistics(self):
        """Test getting duplicate statistics."""
        entities = [self.entity1, self.entity2, self.entity3]
        relations = [self.relation1, self.relation2]
        
        stats = self.detector.get_duplicate_statistics(entities, relations)
        
        self.assertEqual(stats['total_entities'], 3)
        self.assertEqual(stats['total_relations'], 2)
        self.assertEqual(stats['entity_duplicate_groups'], 1)
        self.assertEqual(stats['relation_duplicate_groups'], 1)
        self.assertEqual(stats['total_entity_duplicates'], 1)
        self.assertEqual(stats['total_relation_duplicates'], 1)
        self.assertGreater(stats['entity_duplicate_percentage'], 0)
        self.assertGreater(stats['relation_duplicate_percentage'], 0)


class TestDuplicateGroup(unittest.TestCase):
    """Test cases for DuplicateGroup."""
    
    def test_duplicate_group_creation(self):
        """Test DuplicateGroup creation."""
        entity = Entity(
            id=1,
            entity_name="Test Entity",
            entity_type="Person",
            description="Test description",
            source_chunk_id=["chunk1"],
            documents_id=[],
            clusters_id=[]
        )
        
        duplicate = Entity(
            id=2,
            entity_name="Test Entity",
            entity_type="Person",
            description="Test description",
            source_chunk_id=["chunk2"],
            documents_id=[],
            clusters_id=[]
        )
        
        group = DuplicateGroup(
            primary_item=entity,
            duplicates=[duplicate],
            similarity_score=0.95,
            merge_strategy="name_based"
        )
        
        self.assertEqual(group.primary_item, entity)
        self.assertEqual(len(group.duplicates), 1)
        self.assertEqual(group.duplicates[0], duplicate)
        self.assertEqual(group.similarity_score, 0.95)
        self.assertEqual(group.merge_strategy, "name_based")


if __name__ == '__main__':
    unittest.main()