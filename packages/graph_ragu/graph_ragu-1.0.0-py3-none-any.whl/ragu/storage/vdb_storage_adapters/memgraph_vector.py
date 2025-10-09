"""
Memgraph implementation for BaseVectorStorage.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging
import json
import numpy as np
from datetime import datetime

try:
    import mgclient
except ImportError:
    mgclient = None

from ragu.common.embedder import BaseEmbedder
from ragu.storage.base_storage import BaseVectorStorage


class MemgraphVectorStorage(BaseVectorStorage):
    """
    Memgraph implementation of BaseVectorStorage.
    
    This implementation uses Memgraph's vector indexing capabilities for
    similarity search and vector operations.
    """
    
    def __init__(
        self,
        embedder: BaseEmbedder,
        host: str = "localhost",
        port: int = 7687,
        username: str = "",
        password: str = "",
        database: str = "memgraph",
        use_ssl: bool = False,
        vector_dimension: Optional[int] = None,
        similarity_threshold: float = 0.7,
        batch_size: int = 100
    ):
        """
        Initialize Memgraph vector storage.
        
        Args:
            embedder: Embedder for generating vectors
            host: Memgraph server host
            port: Memgraph server port
            username: Username for authentication
            password: Password for authentication
            database: Database name
            use_ssl: Whether to use SSL connection
            vector_dimension: Dimension of vectors (auto-detected from embedder if None)
            similarity_threshold: Minimum similarity threshold for queries
            batch_size: Batch size for operations
        """
        if mgclient is None:
            raise ImportError("mgclient is required for MemgraphVectorStorage. Install with: pip install mgclient")
        
        self.embedder = embedder
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.use_ssl = use_ssl
        self.vector_dimension = vector_dimension or embedder.dim
        self.similarity_threshold = similarity_threshold
        self.batch_size = batch_size
        
        # Connection object
        self._connection: Optional[mgclient.Connection] = None
        self._cursor: Optional[mgclient.Cursor] = None
        
        # Initialize connection and setup
        self._connect()
        self._setup_vector_index()
    
    def _connect(self) -> None:
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
            self._cursor.execute("RETURN 1")
            self._cursor.fetchall()
        except Exception:
            logging.warning("Connection lost, reconnecting...")
            self._connect()
    
    def _setup_vector_index(self) -> None:
        try:
            index_query = f"""
            CREATE INDEX IF NOT EXISTS vector_index 
            ON :VectorDocument USING vector (embedding, {self.vector_dimension})
            """
            self._execute_query(index_query)
            logging.info("Vector index setup completed")
        except Exception as e:
            logging.warning(f"Vector index setup failed: {e}")
    
    def _execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
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
        elif isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        else:
            return value
    
    def _vector_to_list(self, vector: np.ndarray) -> List[float]:
        """Convert numpy array to list for storage."""
        return vector.tolist()
    
    def _list_to_vector(self, vector_list: List[float]) -> np.ndarray:
        """Convert list to numpy array."""
        return np.array(vector_list)
    
    async def upsert(self, data: Dict[str, Dict[str, Any]]) -> List[Any]:
        """
        Upsert vector documents into Memgraph.
        
        Args:
            data: Dictionary where keys are document IDs and values contain document data
            
        Returns:
            List of upserted document IDs
        """
        if not data:
            logging.warning("Attempted to insert empty data into vector DB.")
            return []
        
        upserted_ids = []
        
        # Process in batches
        items = list(data.items())
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_ids = await self._upsert_batch(batch)
            upserted_ids.extend(batch_ids)
        
        return upserted_ids
    
    async def _upsert_batch(self, batch: List[tuple]) -> List[str]:
        """Upsert a batch of documents."""
        batch_ids = []
        
        for doc_id, doc_data in batch:
            try:
                # Extract content for embedding
                content = doc_data.get("content", "")
                if not content:
                    logging.warning(f"No content found for document {doc_id}")
                    continue
                
                # Generate embedding
                embedding = self.embedder(content)
                if isinstance(embedding, np.ndarray) and embedding.ndim > 1:
                    embedding = embedding[0]  # Take first embedding if batch
                
                # Prepare document properties
                properties = {
                    "id": doc_id,
                    "content": content,
                    "embedding": self._vector_to_list(embedding),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Add other properties from doc_data
                for key, value in doc_data.items():
                    if key != "content" and key != "embedding":
                        properties[key] = value
                
                # Upsert document
                query = """
                MERGE (d:VectorDocument {id: $id})
                SET d += $properties
                """
                
                self._execute_query(query, {
                    "id": doc_id,
                    "properties": properties
                })
                
                batch_ids.append(doc_id)
                
            except Exception as e:
                logging.error(f"Failed to upsert document {doc_id}: {e}")
                continue
        
        return batch_ids
    
    async def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query similar documents using vector similarity.
        
        Args:
            query: Query text
            top_k: Number of top results to return
            
        Returns:
            List of similar documents with similarity scores
        """
        try:
            # Generate embedding for query
            query_embedding = self.embedder(query)
            if isinstance(query_embedding, np.ndarray) and query_embedding.ndim > 1:
                query_embedding = query_embedding[0]
            
            # Perform vector similarity search
            # Note: This uses a simplified cosine similarity approach
            # In production, you might want to use Memgraph's built-in vector functions
            similarity_query = """
            MATCH (d:VectorDocument)
            WITH d, 
                 gds.similarity.cosine(d.embedding, $query_embedding) as similarity
            WHERE similarity >= $threshold
            RETURN d, similarity
            ORDER BY similarity DESC
            LIMIT $top_k
            """
            
            results = self._execute_query(similarity_query, {
                "query_embedding": self._vector_to_list(query_embedding),
                "threshold": self.similarity_threshold,
                "top_k": top_k
            })
            
            # Format results
            formatted_results = []
            for result in results:
                doc_data = result["col_0"]
                similarity = result["col_1"]
                
                formatted_result = {
                    "id": doc_data["properties"]["id"],
                    "content": doc_data["properties"].get("content", ""),
                    "similarity": similarity,
                    "distance": 1.0 - similarity,  # Convert similarity to distance
                    **{k: v for k, v in doc_data["properties"].items() 
                       if k not in ["id", "content", "embedding"]}
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logging.error(f"Query failed: {e}")
            # Fallback to simple text search if vector search fails
            return await self._fallback_text_search(query, top_k)
    
    async def _fallback_text_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback text search when vector search fails."""
        try:
            text_query = """
            MATCH (d:VectorDocument)
            WHERE d.content CONTAINS $query_text
            RETURN d
            ORDER BY d.created_at DESC
            LIMIT $top_k
            """
            
            results = self._execute_query(text_query, {
                "query_text": query,
                "top_k": top_k
            })
            
            formatted_results = []
            for result in results:
                doc_data = result["col_0"]
                formatted_result = {
                    "id": doc_data["properties"]["id"],
                    "content": doc_data["properties"].get("content", ""),
                    "similarity": 0.5,  # Default similarity for text search
                    "distance": 0.5,
                    **{k: v for k, v in doc_data["properties"].items() 
                       if k not in ["id", "content", "embedding"]}
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logging.error(f"Fallback text search failed: {e}")
            return []
    
    async def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        query = "MATCH (d:VectorDocument {id: $id}) RETURN d"
        results = self._execute_query(query, {"id": doc_id})
        
        if not results:
            return None
        
        doc_data = results[0]["col_0"]
        return {
            "id": doc_data["properties"]["id"],
            "content": doc_data["properties"].get("content", ""),
            **{k: v for k, v in doc_data["properties"].items() 
               if k not in ["id", "content", "embedding"]}
        }
    
    async def delete_by_id(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        query = "MATCH (d:VectorDocument {id: $id}) DELETE d"
        try:
            self._execute_query(query, {"id": doc_id})
            return True
        except Exception as e:
            logging.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents."""
        query = "MATCH (d:VectorDocument) RETURN d"
        results = self._execute_query(query)
        
        documents = []
        for result in results:
            doc_data = result["col_0"]
            document = {
                "id": doc_data["properties"]["id"],
                "content": doc_data["properties"].get("content", ""),
                **{k: v for k, v in doc_data["properties"].items() 
                   if k not in ["id", "content", "embedding"]}
            }
            documents.append(document)
        
        return documents
    
    async def get_document_count(self) -> int:
        """Get total number of documents."""
        query = "MATCH (d:VectorDocument) RETURN count(d) as count"
        results = self._execute_query(query)
        return results[0]["col_0"] if results else 0
    
    async def clear_all(self) -> None:
        """Clear all documents."""
        query = "MATCH (d:VectorDocument) DELETE d"
        self._execute_query(query)
        logging.info("All documents cleared from vector storage")
    
    async def index_done_callback(self) -> None:
        """Called when indexing is complete."""
        # Refresh indexes
        try:
            refresh_query = "CALL db.index.fulltext.refresh()"
            self._execute_query(refresh_query)
        except Exception as e:
            logging.debug(f"Index refresh skipped: {e}")
    
    async def close(self) -> None:
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