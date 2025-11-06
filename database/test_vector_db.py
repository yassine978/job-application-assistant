"""Test Chroma vector database."""

from database.vector_db_manager import vector_db
import numpy as np

def test_vector_db():
    """Test vector database operations."""
    print("=" * 60)
    print("Testing Vector Database (Chroma)")
    print("=" * 60)
    
    try:
        # Initialize
        vector_db.initialize()
        
        # Test adding a document
        print("\n📝 Testing document addition...")
        
        test_doc = ["This is a test job posting for a Python developer"]
        test_embedding = [np.random.rand(384).tolist()]  # Random 384-dim vector
        test_metadata = [{"source": "test", "type": "job"}]
        
        ids = vector_db.add_documents(
            collection_name="job_descriptions",
            documents=test_doc,
            embeddings=test_embedding,
            metadatas=test_metadata
        )
        
        print(f"  ✓ Added document with ID: {ids[0]}")
        
        # Test querying
        print("\n🔍 Testing document query...")
        
        results = vector_db.query_collection(
            collection_name="job_descriptions",
            query_embeddings=test_embedding,
            n_results=1
        )
        
        print(f"  ✓ Found {len(results['documents'][0])} result(s)")
        print(f"  ✓ Document: {results['documents'][0][0][:50]}...")
        
        # Test collection counts
        print("\n📊 Collection Statistics:")
        for collection_name in vector_db.collections.keys():
            count = vector_db.get_collection_count(collection_name)
            print(f"  • {collection_name}: {count} documents")
        
        print("\n✅ Vector database test successful!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Vector database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_vector_db()