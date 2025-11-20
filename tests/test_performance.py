"""Performance benchmarks for critical operations."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from datetime import datetime


def benchmark(name: str, target_ms: int = None):
    """Decorator to benchmark a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n[*] Benchmarking: {name}")
            start = time.time()
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start) * 1000

            status = "[OK]"
            if target_ms and elapsed_ms > target_ms:
                status = "[SLOW]"

            print(f"{status} Completed in {elapsed_ms:.2f}ms", end="")
            if target_ms:
                print(f" (target: {target_ms}ms)")
            else:
                print()

            return result, elapsed_ms
        return wrapper
    return decorator


@benchmark("Embedding Generation", target_ms=500)
def test_embedding_performance():
    """Test embedding generation speed."""
    from ai_generation.embeddings.embedding_generator import embedding_generator
    embedding_generator.initialize()

    text = "Machine Learning Engineer with 5 years of experience in Python and TensorFlow"
    embedding = embedding_generator.embed_text(text)

    assert len(embedding) == 384, "Wrong embedding dimension"
    return True


@benchmark("README Parsing", target_ms=100)
def test_parsing_performance():
    """Test README parsing speed."""
    from processing.project_parser import project_parser
    project_parser.initialize()

    readme = """
# Test Project

A test project with Python and ML.

## Features
- Feature 1
- Feature 2

## Technologies
Python, TensorFlow, Flask
"""

    result = project_parser.parse_readme(readme)
    assert 'title' in result
    return True


@benchmark("Job Filtering (100 jobs)", target_ms=200)
def test_filtering_performance():
    """Test job filtering speed."""
    from processing.filter_engine import filter_engine
    filter_engine.initialize()

    # Create 100 mock jobs
    jobs = []
    for i in range(100):
        jobs.append({
            'id': f'job-{i}',
            'job_title': f'Engineer {i}',
            'company_name': f'Company {i}',
            'location': 'Paris' if i % 2 == 0 else 'Remote',
            'job_type': 'Full-time',
            'description': 'Test job',
            'required_skills': ['Python', 'SQL'],
            'posted_date': datetime.utcnow()
        })

    filtered = filter_engine.filter_jobs(
        jobs=jobs,
        keywords='Engineer',
        location='Paris',
        job_types=['Full-time'],
        max_age_days=30
    )

    assert len(filtered) > 0
    return True


@benchmark("CSV Export (50 jobs)", target_ms=150)
def test_csv_export_performance():
    """Test CSV export speed."""
    from output.csv_exporter import csv_exporter

    jobs = []
    for i in range(50):
        jobs.append({
            'job_title': f'Job {i}',
            'company_name': f'Company {i}',
            'match_score': 70 + i % 30,
            'location': 'Paris',
            'job_type': 'Full-time'
        })

    csv_path = csv_exporter.export_search_results(jobs)
    assert csv_path.exists()
    return True


@benchmark("Excel Export (5 sheets)", target_ms=1000)
def test_excel_export_performance():
    """Test Excel export speed."""
    from output.excel_exporter import excel_exporter

    search_results = [{'job_title': 'Job', 'match_score': 80}]
    applications = [{
        'job': search_results[0],
        'cv': {'content': '# CV', 'metadata': {'cv_length': 1}},
        'generated_at': datetime.utcnow()
    }]
    projects = [{'id': '1', 'title': 'Project', 'technologies': ['Python']}]

    excel_path = excel_exporter.export_comprehensive_report(
        search_results=search_results,
        applications=applications,
        projects=projects,
        usage_stats={'1': 1},
        skill_counts={'Python': 1},
        user_skills=['Python'],
        user_name="Test"
    )

    assert excel_path.exists()
    return True


def run_all_tests():
    """Run all performance benchmarks."""
    print("=" * 70)
    print("PERFORMANCE BENCHMARK SUITE")
    print("=" * 70)
    print("Target times are maximum acceptable performance")

    benchmarks = [
        test_embedding_performance,
        test_parsing_performance,
        test_filtering_performance,
        test_csv_export_performance,
        test_excel_export_performance
    ]

    results = []
    for bench in benchmarks:
        try:
            success, elapsed_ms = bench()
            results.append((bench.__name__, success, elapsed_ms))
        except Exception as e:
            print(f"[ERROR] {bench.__name__}: {e}")
            results.append((bench.__name__, False, 0))

    # Summary
    print("\n" + "=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)

    total_time = sum(elapsed for _, _, elapsed in results)
    passed = sum(1 for _, success, _ in results if success)

    print(f"\nTotal Benchmarks: {len(results)}")
    print(f"[OK] Passed: {passed}/{len(results)}")
    print(f"[!] Total Time: {total_time:.2f}ms")

    print(f"\nDetailed Results:")
    for name, success, elapsed in results:
        status = "[OK]" if success else "[X]"
        print(f"  {status} {name}: {elapsed:.2f}ms")

    return passed == len(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
