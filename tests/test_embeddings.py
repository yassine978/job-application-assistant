"""Test embedding generation."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_generation.embeddings.embedding_generator import embedding_generator
import numpy as np

def test_embedding_generator():
    """Test embedding generation functionality."""
    print("=" * 60)
    print("Testing Embedding Generator")
    print("=" * 60)
    
    try:
        # Initialize
        embedding_generator.initialize()
        
        # Test 1: Single text embedding
        print("\n[*] Test 1: Single text embedding")
        text = "Python developer with machine learning experience"
        embedding = embedding_generator.embed_text(text)
        
        print(f"  Input: '{text}'")
        print(f"  Embedding dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        
        assert len(embedding) == 384, f"Expected 384 dimensions, got {len(embedding)}"
        print("  [OK] Single embedding works")
        
        # Test 2: Batch embeddings
        print("\n[*] Test 2: Batch embeddings")
        texts = [
            "Python developer",
            "Machine learning engineer",
            "Frontend developer"
        ]
        embeddings = embedding_generator.embed_texts(texts)
        
        print(f"  Input: {len(texts)} texts")
        print(f"  Output: {len(embeddings)} embeddings")
        print(f"  Each dimension: {len(embeddings[0])}")
        
        assert len(embeddings) == len(texts), "Mismatch in batch size"
        print("  [OK] Batch embedding works")
        
        # Test 3: Profile embedding
        print("\n[*] Test 3: Profile embedding")
        profile_data = {
            'skills': ['Python', 'TensorFlow', 'SQL'],
            'experience': [{
                'title': 'Data Scientist',
                'company': 'Tech Corp'
            }],
            'education': {
                'degree': 'Master',
                'field': 'Computer Science'
            },
            'languages': ['English', 'French']
        }
        
        profile_embedding = embedding_generator.embed_profile(profile_data)
        print(f"  Profile embedded")
        print(f"  Embedding dimension: {len(profile_embedding)}")
        
        assert len(profile_embedding) == 384, "Profile embedding dimension error"
        print("  [OK] Profile embedding works")
        
        # Test 4: Job embedding
        print("\n[*] Test 4: Job embedding")
        job_data = {
            'job_title': 'Senior Python Developer',
            'company_name': 'Google',
            'location': 'Paris',
            'description': 'Looking for an experienced Python developer...',
            'required_skills': ['Python', 'Django', 'PostgreSQL']
        }
        
        job_embedding = embedding_generator.embed_job(job_data)
        print(f"  Job embedded")
        print(f"  Embedding dimension: {len(job_embedding)}")
        
        assert len(job_embedding) == 384, "Job embedding dimension error"
        print("  [OK] Job embedding works")
        
        # Test 5: Project embedding
        print("\n[*] Test 5: Project embedding")
        project_data = {
            'title': 'E-Commerce Platform',
            'description': 'Built a full-stack e-commerce application',
            'technologies': ['React', 'Node.js', 'MongoDB'],
            'highlights': ['Handled 10k users', 'Increased sales by 30%']
        }
        
        project_embedding = embedding_generator.embed_project(project_data)
        print(f"  Project embedded")
        print(f"  Embedding dimension: {len(project_embedding)}")
        
        assert len(project_embedding) == 384, "Project embedding dimension error"
        print("  [OK] Project embedding works")
        
        # Test 6: Similarity calculation
        print("\n[*] Test 6: Similarity calculation")
        text1 = "Python machine learning"
        text2 = "Python ML engineer"
        text3 = "Frontend JavaScript developer"
        
        emb1 = embedding_generator.embed_text(text1)
        emb2 = embedding_generator.embed_text(text2)
        emb3 = embedding_generator.embed_text(text3)
        
        sim_12 = embedding_generator.calculate_similarity(emb1, emb2)
        sim_13 = embedding_generator.calculate_similarity(emb1, emb3)
        
        print(f"  Similarity('Python ML', 'Python ML engineer'): {sim_12:.3f}")
        print(f"  Similarity('Python ML', 'Frontend JS'): {sim_13:.3f}")
        
        assert sim_12 > sim_13, "Similar texts should have higher similarity"
        print("  [OK] Similarity calculation works")

        print("\n[OK] All embedding tests passed!")
        print(f"\n[*] Model Info:")
        print(f"   Model: {embedding_generator.model_name}")
        print(f"   Dimension: {embedding_generator.dimension}")
        print(f"   Ready for semantic search!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all embedding tests."""
    tests = [
        test_embedding_generator
    ]

    passed = sum(1 for test in tests if test())
    failed = len(tests) - passed

    print(f"\n[OK] Passed: {passed}/{len(tests)}")
    print(f"[X] Failed: {failed}/{len(tests)}")

    return failed == 0

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)