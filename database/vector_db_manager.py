"""Chroma vector database management."""

import chromadb
from chromadb.config import Settings
import config
from typing import List, Dict, Optional
import uuid

class VectorDBManager:
    """Manage Chroma vector database operations."""
    
    def __init__(self, persist_directory=None):
        """Initialize Chroma client.
        
        Args:
            persist_directory: Directory for persistent storage
        """
        self.persist_directory = persist_directory or config.CHROMA_PERSIST_DIR
        self.client = None
        self.collections = {}
        self._initialized = False
    
    def initialize(self):
        """Initialize Chroma client and collections."""
        if self._initialized:
            return
        
        # Create client with persistent storage
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        ))
        
        # Create collections
        self._create_collections()
        
        self._initialized = True
        print(f"[OK] Vector database initialized: {self.persist_directory}")
    
    def _create_collections(self):
        """Create all required collections."""
        collection_configs = [
            ("user_profiles", "User profiles with skills and experience"),
            ("user_projects", "User projects with README content"),
            ("job_descriptions", "Job postings and descriptions"),
            ("past_cvs", "Previously generated CVs"),
            ("past_cover_letters", "Previously generated cover letters"),
            ("successful_applications", "High-scoring job applications")
        ]
        
        for name, description in collection_configs:
            try:
                collection = self.client.get_or_create_collection(
                    name=name,
                    metadata={
                        "description": description,
                        "embedding_dimension": config.EMBEDDING_DIMENSION
                    }
                )
                self.collections[name] = collection
                print(f"  [OK] Collection '{name}' ready")
            except Exception as e:
                print(f"  [ERROR] Error creating collection '{name}': {e}")
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
        """
        if not self._initialized:
            self.initialize()
        
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' not found")
        
        collection = self.collections[collection_name]
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # Add to collection
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def query_collection(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """Query a collection for similar documents.
        
        Args:
            collection_name: Name of the collection
            query_embeddings: Query embedding vectors
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Query results with documents, distances, and metadata
        """
        if not self._initialized:
            self.initialize()
        
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' not found")
        
        collection = self.collections[collection_name]
        
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where
        )
        
        return results
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents
        """
        if not self._initialized:
            self.initialize()
        
        if collection_name not in self.collections:
            return 0
        
        return self.collections[collection_name].count()
    
    def delete_collection(self, collection_name: str):
        """Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
        """
        if not self._initialized:
            self.initialize()
        
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            print(f"[OK] Collection '{collection_name}' deleted")
        except Exception as e:
            print(f"[ERROR] Error deleting collection '{collection_name}': {e}")
    
    def reset_all_collections(self):
        """Delete and recreate all collections (use with caution!)."""
        if not self._initialized:
            self.initialize()
        
        for collection_name in list(self.collections.keys()):
            self.delete_collection(collection_name)
        
        self._create_collections()
        print("[OK] All collections reset")


# Global vector database instance
vector_db = VectorDBManager()