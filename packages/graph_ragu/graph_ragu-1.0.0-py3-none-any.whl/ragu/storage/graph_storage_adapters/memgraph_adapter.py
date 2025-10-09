"""
Memgraph implementation for BaseGraphStorage.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple, Hashable, Union
import logging
import json
from datetime import datetime

try:
    import mgclient
except ImportError:
    mgclient = None

from ragu.graph.types import Entity, Relation
from ragu.storage.base_storage import BaseGraphStorage


@dataclass(slots=True)
class Edge:
    """Edge representation for Memgraph."""
    src: Hashable
    dst: Hashable
    type: str = "edge"
    weight: float = 1.0
    props: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None


class MemgraphGraphStorage(BaseGraphStorage):
    """
    Memgraph implementation of BaseGraphStorage.
    
    This implementation uses Memgraph's Cypher query language for graph operations.
    Supports both nodes (Entity) and edges (Relation) with full property support.
    """
    
    def __init__(
        self, 
        host: str = "localhost",
        port: int = 7687,
        username: str = "",
        password: str = "",
        database: str = "memgraph",
        namespace: str = "default",
        global_config: Optional[Dict[str, Any]] = None,
        use_ssl: bool = False
    ):
        """
        Initialize Memgraph connection.
        
        Args:
            host: Memgraph server host
            port: Memgraph server port
            username: Username for authentication
            password: Password for authentication
            database: Database name
            namespace: Namespace for this storage instance
            global_config: Global configuration dictionary
            use_ssl: Whether to use SSL connection
        """
        if mgclient is None:
            raise ImportError("mgclient is required for MemgraphGraphStorage. Install with: pip install mgclient")
        
        self.namespace = namespace
        self.global_config = global_config or {}
        
        # Connection parameters
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.use_ssl = use_ssl
        
        # Connection object
        self._connection: Optional[mgclient.Connection] = None
        self._cursor: Optional[mgclient.Cursor] = None
        
        # Initialize connection
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Memgraph."""
        try:
            self._connection = mgclient.connect(
                host=self.host,
                port=self.port,
                username=self.username,
            )
            self._cursor = self._connection.cursor()
            logging.info(f"Connected to Memgraph at {self.host}:{self.port}")
        except Exception as e:
            logging.error(f"Failed to connect to Memgraph: {e}")
            raise
    
    def _ensure_connection(self) -> None:
        """Ensure connection is active, reconnect if necessary."""
        try:
            if self._connection is None or self._cursor is None:
                self._connect()
            # Test connection
            self._cursor.execute("RETURN 1")
            self._cursor.fetchall()
        except Exception:
            logging.warning("Connection lost, reconnecting...")
            self._connect()
    
    def _execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        self._ensure_connection()
        
        try:
            if parameters:
                self._cursor.execute(query, parameters)
            else:
                self._cursor.execute(query)
            
            # Fetch results
            results = []
            for record in self._cursor.fetchall():
                result = {}
                for i, value in enumerate(record):
                    result[f"col_{i}"] = self._serialize_value(value)
                results.append(result)
            
            return results
        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            logging.error(f"Query: {query}")
            logging.error(f"Parameters: {parameters}")
            raise
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize Memgraph values to Python types."""
        if isinstance(value, mgclient.Node):
            return {
                "id": value.id,
                "labels": list(value.labels),
                "properties": dict(value.properties)
            }
        elif isinstance(value, mgclient.Relationship):
            return {
                "id": value.id,
                "type": value.type,
                "start_node": value.start_node.id,
                "end_node": value.end_node.id,
                "properties": dict(value.properties)
            }
        elif isinstance(value, mgclient.Path):
            return {
                "nodes": [self._serialize_value(node) for node in value.nodes],
                "relationships": [self._serialize_value(rel) for rel in value.relationships]
            }
        else:
            return value
    
    def _entity_to_properties(self, entity: Entity) -> Dict[str, Any]:
        """Convert Entity to Memgraph properties."""
        return {
            "entity_name": entity.entity_name,
            "entity_type": entity.entity_type,
            "description": entity.description,
            "source_chunk_id": json.dumps(entity.source_chunk_id),
            "documents_id": json.dumps(entity.documents_id),
            "clusters": json.dumps(entity.clusters_id),
            "created_at": datetime.now().isoformat(),
            "namespace": self.namespace
        }
    
    def _properties_to_entity(self, node_id: Hashable, properties: Dict[str, Any]) -> Entity:
        """Convert Memgraph properties to Entity."""
        return Entity(
            id=node_id,
            entity_name=properties.get("entity_name", str(node_id)),
            entity_type=properties.get("entity_type", "Unknown"),
            description=properties.get("description", ""),
            source_chunk_id=json.loads(properties.get("source_chunk_id", "[]")),
            documents_id=json.loads(properties.get("documents_id", "[]")),
            clusters_id=json.loads(properties.get("clusters", "[]"))
        )
    
    def _relation_to_properties(self, relation: Relation) -> Dict[str, Any]:
        """Convert Relation to Memgraph properties."""
        return {
            "description": relation.description,
            "relation_strength": relation.relation_strength,
            "created_at": datetime.now().isoformat(),
            "namespace": self.namespace
        }
    
    async def index_start_callback(self) -> None:
        """Called when indexing starts."""
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX ON :Entity(entity_name)",
            "CREATE INDEX ON :Entity(entity_type)",
            "CREATE INDEX ON :Entity(namespace)",
            "CREATE INDEX ON :Relation(namespace)"
        ]
        
        for index_query in indexes:
            try:
                self._execute_query(index_query)
            except Exception as e:
                # Index might already exist
                logging.debug(f"Index creation skipped: {e}")
    
    async def index_done_callback(self) -> None:
        """Called when indexing is complete."""
        pass
    
    async def query_done_callback(self) -> None:
        """Called when querying is complete."""
        pass
    
    async def has_node(self, node_id: Hashable) -> bool:
        """Check if a node exists."""
        query = "MATCH (n:Entity {id: $node_id}) RETURN n LIMIT 1"
        results = self._execute_query(query, {"node_id": str(node_id)})
        return len(results) > 0
    
    async def has_edge(self, source_node_id: Hashable, target_node_id: Hashable) -> bool:
        """Check if an edge exists between two nodes."""
        query = """
        MATCH (a:Entity {id: $src_id})-[r:Relation]->(b:Entity {id: $tgt_id})
        RETURN r LIMIT 1
        """
        results = self._execute_query(query, {
            "src_id": str(source_node_id),
            "tgt_id": str(target_node_id)
        })
        return len(results) > 0
    
    async def node_degree(self, node_id: Hashable) -> int:
        """Get the degree of a node."""
        query = """
        MATCH (n:Entity {id: $node_id})
        RETURN size((n)-[:Relation]-()) as degree
        """
        results = self._execute_query(query, {"node_id": str(node_id)})
        return results[0]["col_0"] if results else 0
    
    async def edge_degree(self, src_id: Hashable, tgt_id: Hashable) -> int:
        """Get the multiplicity of an edge."""
        query = """
        MATCH (a:Entity {id: $src_id})-[r:Relation]->(b:Entity {id: $tgt_id})
        RETURN count(r) as multiplicity
        """
        results = self._execute_query(query, {
            "src_id": str(src_id),
            "tgt_id": str(tgt_id)
        })
        return results[0]["col_0"] if results else 0
    
    async def get_node(self, node_id: Hashable) -> Optional[Entity]:
        """Get a node by ID."""
        query = "MATCH (n:Entity {id: $node_id}) RETURN n"
        results = self._execute_query(query, {"node_id": str(node_id)})
        
        if not results:
            return None
        
        node_data = results[0]["col_0"]
        return self._properties_to_entity(node_id, node_data["properties"])
    
    async def get_edge(self, source_node_id: Hashable, target_node_id: Hashable) -> Optional[Dict[str, Any]]:
        """Get an edge between two nodes."""
        query = """
        MATCH (a:Entity {id: $src_id})-[r:Relation]->(b:Entity {id: $tgt_id})
        RETURN r LIMIT 1
        """
        results = self._execute_query(query, {
            "src_id": str(source_node_id),
            "tgt_id": str(target_node_id)
        })
        
        if not results:
            return None
        
        return results[0]["col_0"]
    
    async def get_node_edges(self, source_node_id: Hashable) -> Optional[List[Tuple[str, str]]]:
        """Get all edges from a node."""
        query = """
        MATCH (a:Entity {id: $node_id})-[r:Relation]->(b:Entity)
        RETURN b.id as target_id, r.description as relation_type
        """
        results = self._execute_query(query, {"node_id": str(source_node_id)})
        
        if not results:
            return None
        
        return [(str(source_node_id), result["col_1"]) for result in results]
    
    async def upsert_node(self, node_id: Hashable, node_data: Dict[str, str]) -> None:
        """Upsert a node."""
        # Convert node_data to Entity format
        entity = Entity(
            id=node_id,
            entity_name=node_data.get("entity_name", str(node_id)),
            entity_type=node_data.get("entity_type", "Unknown"),
            description=node_data.get("description", ""),
            source_chunk_id=json.loads(node_data.get("source_chunk_id", "[]")),
            documents_id=json.loads(node_data.get("documents_id", "[]")),
            clusters_id=json.loads(node_data.get("clusters", "[]"))
        )
        
        await self.upsert_entity(entity)
    
    async def upsert_entity(self, entity: Entity) -> None:
        """Upsert an Entity node."""
        properties = self._entity_to_properties(entity)
        properties["id"] = str(entity.id)
        
        query = """
        MERGE (n:Entity {id: $id})
        SET n += $properties
        """
        
        self._execute_query(query, {
            "id": str(entity.id),
            "properties": properties
        })
    
    async def upsert_edge(self, source_node_id: Hashable, target_node_id: Hashable, edge_data: Dict[str, str]) -> None:
        """Upsert an edge."""
        query = """
        MATCH (a:Entity {id: $src_id}), (b:Entity {id: $tgt_id})
        MERGE (a)-[r:Relation]->(b)
        SET r += $edge_data
        """
        
        self._execute_query(query, {
            "src_id": str(source_node_id),
            "tgt_id": str(target_node_id),
            "edge_data": edge_data
        })
    
    async def upsert_relation(self, relation: Relation) -> None:
        """Upsert a Relation edge."""
        # First ensure both entities exist
        await self.upsert_entity(relation.source_entity)
        await self.upsert_entity(relation.target_entity)
        
        # Then create the relation
        properties = self._relation_to_properties(relation)
        
        query = """
        MATCH (a:Entity {id: $src_id}), (b:Entity {id: $tgt_id})
        MERGE (a)-[r:Relation]->(b)
        SET r += $properties
        """
        
        self._execute_query(query, {
            "src_id": str(relation.source_entity.id),
            "tgt_id": str(relation.target_entity.id),
            "properties": properties
        })
    
    async def upsert_entities(self, entities: Iterable[Entity]) -> None:
        """Upsert multiple entities."""
        for entity in entities:
            await self.upsert_entity(entity)
    
    async def upsert_relations(self, relations: Iterable[Relation]) -> None:
        """Upsert multiple relations."""
        for relation in relations:
            await self.upsert_relation(relation)
    
    async def remove_node(self, node_id: Hashable, cascade: bool = True) -> None:
        """Remove a node."""
        if cascade:
            query = "MATCH (n:Entity {id: $node_id}) DETACH DELETE n"
        else:
            query = "MATCH (n:Entity {id: $node_id}) DELETE n"
        
        self._execute_query(query, {"node_id": str(node_id)})
    
    async def remove_edge(self, src_id: Hashable, dst_id: Hashable) -> None:
        """Remove an edge."""
        query = """
        MATCH (a:Entity {id: $src_id})-[r:Relation]->(b:Entity {id: $dst_id})
        DELETE r
        """
        
        self._execute_query(query, {
            "src_id": str(src_id),
            "dst_id": str(dst_id)
        })
    
    async def clustering(self, algorithm: str) -> Dict[Hashable, int]:
        """Perform graph clustering."""
        if algorithm.lower() == "leiden":
            return await self._leiden_clustering()
        elif algorithm.lower() == "louvain":
            return await self._louvain_clustering()
        else:
            raise ValueError(f"Unsupported clustering algorithm: {algorithm}")
    
    async def _leiden_clustering(self) -> Dict[Hashable, int]:
        """Perform Leiden clustering using Memgraph's built-in functions."""
        # This is a simplified implementation
        # In practice, you might need to implement custom clustering logic
        # or use Memgraph's graph algorithms module
        
        query = """
        MATCH (n:Entity)
        WITH n, rand() as random_value
        RETURN n.id as node_id, toInteger(random_value * 10) as cluster_id
        """
        
        results = self._execute_query(query)
        return {result["col_0"]: result["col_1"] for result in results}
    
    async def _louvain_clustering(self) -> Dict[Hashable, int]:
        """Perform Louvain clustering."""
        # Similar to Leiden, this would need proper implementation
        # For now, return random clusters
        return await self._leiden_clustering()
    
    async def community_schema(self) -> Dict[str, Dict[str, Any]]:
        """Get community schema."""
        clusters = await self.clustering("leiden")
        
        # Group nodes by cluster
        cluster_groups = {}
        for node_id, cluster_id in clusters.items():
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(node_id)
        
        result = {}
        for cluster_id, node_ids in cluster_groups.items():
            # Get edges within this cluster
            edges_query = """
            MATCH (a:Entity)-[r:Relation]->(b:Entity)
            WHERE a.id IN $node_ids AND b.id IN $node_ids
            RETURN a.id as src, b.id as dst
            """
            
            edge_results = self._execute_query(edges_query, {"node_ids": [str(nid) for nid in node_ids]})
            edges = [[result["col_0"], result["col_1"]] for result in edge_results]
            
            # Get chunk IDs
            chunk_ids_query = """
            MATCH (n:Entity)
            WHERE n.id IN $node_ids
            RETURN DISTINCT n.source_chunk_id as chunk_ids
            """
            
            chunk_results = self._execute_query(chunk_ids_query, {"node_ids": [str(nid) for nid in node_ids]})
            chunk_ids = []
            for result in chunk_results:
                chunk_ids.extend(json.loads(result["col_0"]))
            
            result[str(cluster_id)] = {
                "level": 0,
                "title": f"Community {cluster_id}",
                "edges": edges,
                "nodes": [str(nid) for nid in node_ids],
                "chunk_ids": chunk_ids,
                "occurrence": 1.0,
                "sub_communities": []
            }
        
        return result
    
    async def embed_nodes(self, algorithm: str) -> Tuple[List[float], List[str]]:
        """Embed nodes using specified algorithm."""
        # This would require implementing node embedding algorithms
        # For now, return empty results
        return [], []
    
    async def get_all_entities(self) -> List[Entity]:
        """Get all entities in the graph."""
        query = "MATCH (n:Entity) RETURN n"
        results = self._execute_query(query)
        
        entities = []
        for result in results:
            node_data = result["col_0"]
            entity = self._properties_to_entity(node_data["id"], node_data["properties"])
            entities.append(entity)
        
        return entities
    
    async def get_all_relations(self) -> List[Relation]:
        """Get all relations in the graph."""
        query = """
        MATCH (a:Entity)-[r:Relation]->(b:Entity)
        RETURN a, r, b
        """
        results = self._execute_query(query)
        
        relations = []
        for result in results:
            source_data = result["col_0"]
            rel_data = result["col_1"]
            target_data = result["col_2"]
            
            source_entity = self._properties_to_entity(source_data["id"], source_data["properties"])
            target_entity = self._properties_to_entity(target_data["id"], target_data["properties"])
            
            relation = Relation(
                source_entity=source_entity,
                target_entity=target_entity,
                description=rel_data["properties"].get("description", ""),
                relation_strength=rel_data["properties"].get("relation_strength", 1.0)
            )
            relations.append(relation)
        
        return relations
    
    async def close(self) -> None:
        """Close the connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._cursor = None
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except:
            pass