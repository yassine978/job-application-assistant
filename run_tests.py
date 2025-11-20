"""Master test runner for the entire application."""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def run_test_suite(test_name: str, test_module: str) -> tuple:
    """Run a test suite and return results.

    Args:
        test_name: Display name for the test suite
        test_module: Module path to the test

    Returns:
        Tuple of (passed: bool, message: str)
    """
    print(f"\n{'=' * 70}")
    print(f"Running: {test_name}")
    print(f"{'=' * 70}")

    try:
        # Import and run the test
        module_parts = test_module.rsplit('.', 1)
        if len(module_parts) == 2:
            module_name, function_name = module_parts
            module = __import__(module_name, fromlist=[function_name])
            test_function = getattr(module, function_name)
        else:
            module = __import__(test_module)
            test_function = getattr(module, 'run_all_tests', None)

        if test_function is None:
            return False, f"No test function found in {test_module}"

        result = test_function()

        if result:
            print(f"\n[OK] {test_name} - PASSED")
            return True, "PASSED"
        else:
            print(f"\n[X] {test_name} - FAILED")
            return False, "FAILED"

    except Exception as e:
        print(f"\n[ERROR] {test_name} - ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, f"ERROR: {str(e)}"


def main():
    """Run all test suites."""
    print("=" * 70)
    print("JOB APPLICATION ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Define all test suites
    test_suites = [
        # Phase 3: Embeddings
        ("Embeddings & Vector Store", "tests.test_embeddings.run_all_tests"),

        # Phase 3.5: Project Parser
        ("Project Parser", "tests.test_processing.test_project_parser.run_all_tests"),

        # Phase 4: Web Scraping
        ("Scraper Integration", "tests.test_scrapers.test_scraper_integration.run_all_tests"),

        # Phase 5: RAG Processing
        ("RAG Ranking", "tests.test_processing.test_rag_ranking.run_all_tests"),

        # Phase 6: AI Generation
        ("Document Generation", "tests.test_ai_generation.test_document_generation.run_all_tests"),

        # Phase 7: Authentication
        ("Authentication", "tests.test_dashboard.test_auth.run_all_tests"),

        # Phase 9: Output & Export
        ("Export Functionality", "tests.test_output.test_exports.run_all_tests"),

        # Database Tests
        ("Database Operations", "tests.test_database.run_all_tests"),

        # Vector Integration
        ("Vector Integration", "tests.test_vector_integration.run_all_tests"),
    ]

    # Run all tests
    results = []
    for test_name, test_module in test_suites:
        passed, message = run_test_suite(test_name, test_module)
        results.append((test_name, passed, message))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed, _ in results if passed)
    failed_count = len(results) - passed_count

    print(f"\nTotal Test Suites: {len(results)}")
    print(f"[OK] Passed: {passed_count}")
    print(f"[X] Failed: {failed_count}")

    print(f"\nDetailed Results:")
    for test_name, passed, message in results:
        status = "[OK] PASSED" if passed else "[X] FAILED"
        print(f"  {status} - {test_name}")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Exit code
    if failed_count == 0:
        print("\n[SUCCESS] All test suites passed!")
        sys.exit(0)
    else:
        print(f"\n[FAILURE] {failed_count} test suite(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
