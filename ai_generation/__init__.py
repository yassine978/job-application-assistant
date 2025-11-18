"""AI Generation module for document creation."""

from ai_generation.embeddings.embedding_generator import EmbeddingGenerator, embedding_generator
from ai_generation.embeddings.vector_store import VectorStore, vector_store
from ai_generation.embeddings.retriever import Retriever, retriever
from ai_generation.rag.project_selector import ProjectSelector, project_selector
from ai_generation.rag.page_optimizer import PageOptimizer, page_optimizer
from ai_generation.rag.rag_pipeline import RAGPipeline, rag_pipeline
from ai_generation.cv_generator import CVGenerator, cv_generator
from ai_generation.cover_letter_generator import CoverLetterGenerator, cover_letter_generator

__all__ = [
    'EmbeddingGenerator', 'embedding_generator',
    'VectorStore', 'vector_store',
    'Retriever', 'retriever',
    'ProjectSelector', 'project_selector',
    'PageOptimizer', 'page_optimizer',
    'RAGPipeline', 'rag_pipeline',
    'CVGenerator', 'cv_generator',
    'CoverLetterGenerator', 'cover_letter_generator'
]
