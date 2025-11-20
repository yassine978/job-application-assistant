"""Generate embeddings from text using sentence-transformers."""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import config

class EmbeddingGenerator:
    """Generate embeddings using HuggingFace sentence-transformers."""
    
    def __init__(self, model_name=None):
        """Initialize the embedding model.
        
        Args:
            model_name: HuggingFace model name (uses config default if not provided)
        """
        self.model_name = model_name or config.EMBEDDING_MODEL
        self.model = None
        self.dimension = config.EMBEDDING_DIMENSION
        self._initialized = False
    
    def initialize(self):
        """Load the embedding model."""
        if self._initialized:
            return
        
        print(f"[*] Loading embedding model: {self.model_name}")
        print("   This may take a minute on first run (downloading ~90MB)...")
        
        # Load model
        self.model = SentenceTransformer(self.model_name)
        
        self._initialized = True
        print(f"[OK] Embedding model loaded: {self.model_name}")
        print(f"   Embedding dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats (embedding vector)
        """
        if not self._initialized:
            self.initialize()
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self._initialized:
            self.initialize()
        
        # Batch encoding is faster
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        return embeddings.tolist()
    
    def embed_profile(self, profile_data: dict) -> List[float]:
        """Generate embedding for a user profile.
        
        Args:
            profile_data: Dictionary with profile information
            
        Returns:
            Embedding vector
        """
        # Combine profile data into single text
        profile_text = self._format_profile_text(profile_data)
        
        return self.embed_text(profile_text)
    
    def embed_job(self, job_data: dict) -> List[float]:
        """Generate embedding for a job posting.
        
        Args:
            job_data: Dictionary with job information
            
        Returns:
            Embedding vector
        """
        # Combine job data into single text
        job_text = self._format_job_text(job_data)
        
        return self.embed_text(job_text)
    
    def embed_project(self, project_data: dict) -> List[float]:
        """Generate embedding for a project.
        
        Args:
            project_data: Dictionary with project information
            
        Returns:
            Embedding vector
        """
        # Combine project data into single text
        project_text = self._format_project_text(project_data)
        
        return self.embed_text(project_text)
    
    def _format_profile_text(self, profile_data: dict) -> str:
        """Format profile data into text for embedding.
        
        Args:
            profile_data: Profile dictionary
            
        Returns:
            Formatted text
        """
        parts = []
        
        # Add skills
        if profile_data.get('skills'):
            skills_text = ', '.join(profile_data['skills'])
            parts.append(f"Skills: {skills_text}")
        
        # Add experience
        if profile_data.get('experience'):
            exp = profile_data['experience']
            if isinstance(exp, dict):
                if exp.get('roles'):
                    for role in exp['roles']:
                        parts.append(f"Experience: {role.get('title', '')} at {role.get('company', '')}")
            elif isinstance(exp, list):
                for role in exp:
                    parts.append(f"Experience: {role.get('title', '')} at {role.get('company', '')}")
        
        # Add education
        if profile_data.get('education'):
            edu = profile_data['education']
            if isinstance(edu, dict):
                parts.append(f"Education: {edu.get('degree', '')} in {edu.get('field', '')}")
            elif isinstance(edu, list):
                for degree in edu:
                    parts.append(f"Education: {degree.get('degree', '')} in {degree.get('field', '')}")
        
        # Add languages
        if profile_data.get('languages'):
            langs_text = ', '.join(profile_data['languages'])
            parts.append(f"Languages: {langs_text}")
        
        return '. '.join(parts)
    
    def _format_job_text(self, job_data: dict) -> str:
        """Format job data into text for embedding.
        
        Args:
            job_data: Job dictionary
            
        Returns:
            Formatted text
        """
        parts = []
        
        # Add title and company
        if job_data.get('job_title'):
            parts.append(f"Job Title: {job_data['job_title']}")
        
        if job_data.get('company_name'):
            parts.append(f"Company: {job_data['company_name']}")
        
        # Add location
        if job_data.get('location'):
            parts.append(f"Location: {job_data['location']}")
        
        # Add job type
        if job_data.get('job_type'):
            parts.append(f"Type: {job_data['job_type']}")
        
        # Add description
        if job_data.get('description'):
            # Truncate long descriptions
            desc = job_data['description'][:500]
            parts.append(f"Description: {desc}")
        
        # Add required skills
        if job_data.get('required_skills'):
            skills_text = ', '.join(job_data['required_skills'])
            parts.append(f"Required Skills: {skills_text}")
        
        return '. '.join(parts)
    
    def _format_project_text(self, project_data: dict) -> str:
        """Format project data into text for embedding.
        
        Args:
            project_data: Project dictionary
            
        Returns:
            Formatted text
        """
        parts = []
        
        # Add title
        if project_data.get('title'):
            parts.append(f"Project: {project_data['title']}")
        
        # Add description
        if project_data.get('description'):
            parts.append(f"Description: {project_data['description']}")
        
        # Add technologies
        if project_data.get('technologies'):
            tech_text = ', '.join(project_data['technologies'])
            parts.append(f"Technologies: {tech_text}")
        
        # Add highlights
        if project_data.get('highlights'):
            highlights_text = '. '.join(project_data['highlights'])
            parts.append(f"Highlights: {highlights_text}")
        
        # Add README excerpt (first 300 chars)
        if project_data.get('readme_content'):
            readme_excerpt = project_data['readme_content'][:300]
            parts.append(f"Details: {readme_excerpt}")
        
        return '. '.join(parts)
    
    def calculate_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0 to 1, higher = more similar)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Convert to 0-1 range (cosine is -1 to 1)
        similarity = (similarity + 1) / 2
        
        return float(similarity)


# Global embedding generator instance
embedding_generator = EmbeddingGenerator()