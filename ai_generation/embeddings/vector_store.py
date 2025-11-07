"""Integration between embeddings and Chroma vector store."""

from typing import List, Dict, Optional
from database.vector_db_manager import vector_db
from ai_generation.embeddings.embedding_generator import embedding_generator

class VectorStore:
    """High-level interface for storing and retrieving embeddings."""
    
    def __init__(self):
        """Initialize vector store."""
        self.vector_db = vector_db
        self.embedding_gen = embedding_generator
    
    def initialize(self):
        """Initialize both vector DB and embedding generator."""
        self.vector_db.initialize()
        self.embedding_gen.initialize()
        print("✅ Vector store initialized")
    
    def add_profile(
        self, 
        user_id: str, 
        profile_data: dict
    ) -> str:
        """Add user profile to vector store.
        
        Args:
            user_id: User ID
            profile_data: Profile dictionary
            
        Returns:
            Document ID in Chroma
        """
        # Generate embedding
        embedding = self.embedding_gen.embed_profile(profile_data)
        
        # Format text
        text = self.embedding_gen._format_profile_text(profile_data)
        
        # Add to Chroma
        ids = self.vector_db.add_documents(
            collection_name="user_profiles",
            documents=[text],
            embeddings=[embedding],
            metadatas=[{
                "user_id": user_id,
                "type": "profile"
            }],
            ids=[user_id]  # Use user_id as document ID
        )
        
        return ids[0]
    
    def add_project(
        self, 
        project_id: str, 
        user_id: str,
        project_data: dict
    ) -> str:
        """Add project to vector store.
        
        Args:
            project_id: Project ID
            user_id: User ID
            project_data: Project dictionary
            
        Returns:
            Document ID in Chroma
        """
        # Generate embedding
        embedding = self.embedding_gen.embed_project(project_data)
        
        # Format text
        text = self.embedding_gen._format_project_text(project_data)
        
        # Add to Chroma
        ids = self.vector_db.add_documents(
            collection_name="user_projects",
            documents=[text],
            embeddings=[embedding],
            metadatas=[{
                "project_id": project_id,
                "user_id": user_id,
                "title": project_data.get('title', '')
            }],
            ids=[project_id]
        )
        
        return ids[0]
    
    def add_job(
        self, 
        job_id: str, 
        job_data: dict
    ) -> str:
        """Add job to vector store.
        
        Args:
            job_id: Job ID
            job_data: Job dictionary
            
        Returns:
            Document ID in Chroma
        """
        # Generate embedding
        embedding = self.embedding_gen.embed_job(job_data)
        
        # Format text
        text = self.embedding_gen._format_job_text(job_data)
        
        # Add to Chroma
        ids = self.vector_db.add_documents(
            collection_name="job_descriptions",
            documents=[text],
            embeddings=[embedding],
            metadatas=[{
                "job_id": job_id,
                "company": job_data.get('company_name', ''),
                "title": job_data.get('job_title', ''),
                "location": job_data.get('location', '')
            }],
            ids=[job_id]
        )
        
        return ids[0]
    
    def find_similar_jobs(
        self, 
        user_id: str, 
        n_results: int = 10
    ) -> List[Dict]:
        """Find jobs similar to user's profile.
        
        Args:
            user_id: User ID
            n_results: Number of results to return
            
        Returns:
            List of similar jobs with scores
        """
        # Get user profile embedding from Chroma
        try:
            # Query to get the stored profile document
            profile_results = self.vector_db.collections["user_profiles"].get(
                ids=[user_id],
                include=["embeddings"]
            )
            
            # Check if we got results
            if not profile_results['ids'] or len(profile_results['embeddings']) == 0:
                print(f"⚠️  No profile embedding found for user: {user_id}")
                return []
            
            # Get the profile embedding
            profile_embedding = profile_results['embeddings'][0]
            
        except Exception as e:
            print(f"❌ Error getting profile embedding: {e}")
            return []
        
        # Find similar jobs
        job_results = self.vector_db.query_collection(
            collection_name="job_descriptions",
            query_embeddings=[profile_embedding],
            n_results=n_results
        )
        
        # Format results
        similar_jobs = []
        if job_results['ids'] and len(job_results['ids']) > 0:
            for i, job_id in enumerate(job_results['ids'][0]):
                distance = job_results['distances'][0][i]  # ← ADD THIS LINE
                similarity = 1 / (1 + distance)  # ← ADD THIS LINE
                similar_jobs.append({
                    'job_id': job_id,
                    'similarity': similarity,
                    'metadata': job_results['metadatas'][0][i]
                })
        
        return similar_jobs


    def find_relevant_projects(
        self, 
        job_id: str,
        user_id: str,
        n_results: int = 5
    ) -> List[Dict]:
        """Find user's projects relevant to a job.
        
        Args:
            job_id: Job ID
            user_id: User ID
            n_results: Number of projects to return
            
        Returns:
            List of relevant projects with scores
        """
        # Get job embedding
        try:
            job_results = self.vector_db.collections["job_descriptions"].get(
                ids=[job_id],
                include=["embeddings"]
            )
            
            # Check if we got results
            if not job_results['ids'] or len(job_results['embeddings']) == 0:
                print(f"⚠️  No job embedding found for job: {job_id}")
                return []
            
            job_embedding = job_results['embeddings'][0]
            
        except Exception as e:
            print(f"❌ Error getting job embedding: {e}")
            return []
        
        # Find relevant projects for this user
        project_results = self.vector_db.query_collection(
            collection_name="user_projects",
            query_embeddings=[job_embedding],
            n_results=n_results,
            where={"user_id": user_id}
        )
        
        # Format results
        relevant_projects = []
        if project_results['ids'] and len(project_results['ids']) > 0:
            for i, project_id in enumerate(project_results['ids'][0]):
                distance = project_results['distances'][0][i]  # ← ADD THIS LINE
                relevance = 1 / (1 + distance)  # ← ADD THIS LINE
                relevant_projects.append({
                    'project_id': project_id,
                    'relevance': relevance,  # ← CHANGE THIS LINE
                    'metadata': project_results['metadatas'][0][i]
                })
        
        return relevant_projects


# Global vector store instance
vector_store = VectorStore()