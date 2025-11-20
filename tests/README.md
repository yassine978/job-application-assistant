# Test Suite Documentation

## Overview

Comprehensive test suite for the Job Application Assistant covering all phases of development.

## Test Structure

```
tests/
├── test_embeddings.py              # Phase 3: Vector embeddings
├── test_processing/
│   ├── test_project_parser.py      # Phase 3.5: README parsing
│   └── test_rag_ranking.py         # Phase 5: RAG ranking
├── test_scrapers/
│   └── test_scraper_integration.py # Phase 4: Web scraping
├── test_ai_generation/
│   └── test_document_generation.py # Phase 6: CV/letter generation
├── test_dashboard/
│   └── test_auth.py                # Phase 7: Authentication
├── test_output/
│   └── test_exports.py             # Phase 9: CSV/Excel/PDF export
├── test_database.py                # Database operations
├── test_vector_integration.py      # Vector store integration
├── test_integration.py             # End-to-end workflows
└── test_performance.py             # Performance benchmarks
```

## Running Tests

### Run All Tests

```bash
# Run master test suite
python run_tests.py

# Run with pytest
pytest tests/

# Run with coverage
pytest --cov=. --cov-report=html tests/
```

### Run Specific Test Suites

```bash
# Phase-specific tests
python tests/test_embeddings.py
python tests/test_processing/test_project_parser.py
python tests/test_dashboard/test_auth.py
python tests/test_output/test_exports.py

# Integration tests
python tests/test_integration.py

# Performance benchmarks
python tests/test_performance.py
```

### Run with Pytest Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"

# Skip tests requiring database
pytest -m "not requires_db"
```

## Test Categories

### Unit Tests
Fast, isolated tests for individual components.

**Examples:**
- `test_embeddings.py`: Test embedding generation
- `test_project_parser.py`: Test README parsing
- `test_exports.py`: Test CSV/Excel export

**Run time:** <1 second per test

### Integration Tests
Tests that verify multiple components working together.

**Examples:**
- `test_integration.py`: Complete workflow from registration to export
- `test_vector_integration.py`: Vector store operations
- `test_rag_ranking.py`: RAG pipeline end-to-end

**Run time:** 1-10 seconds per test

### Performance Tests
Benchmarks to ensure critical operations meet performance targets.

**Examples:**
- Embedding generation: <500ms
- README parsing: <100ms
- Job filtering (100 jobs): <200ms
- CSV export (50 jobs): <150ms
- Excel export (5 sheets): <1000ms

**Run time:** Varies by benchmark

## Test Coverage

### Current Coverage by Phase

| Phase | Component | Tests | Coverage |
|-------|-----------|-------|----------|
| 2 | Database | ✅ Yes | Basic |
| 3 | Embeddings | ✅ Yes | Comprehensive |
| 3.5 | Project Parser | ✅ Yes | Comprehensive |
| 4 | Scrapers | ✅ Yes | Integration |
| 5 | RAG Ranking | ✅ Yes | Comprehensive |
| 6 | AI Generation | ✅ Yes | Comprehensive |
| 7 | Authentication | ✅ Yes | Comprehensive |
| 8 | Dashboard | ⚠️ Partial | UI tests limited |
| 9 | Export | ✅ Yes | Comprehensive |

### Code Coverage Goals

- **Unit Tests:** >80% line coverage
- **Integration Tests:** All critical paths covered
- **Performance Tests:** All bottleneck operations benchmarked

## Test Data

### Mock Data
Tests use mock data to avoid external dependencies:
- Mock jobs (no real scraping)
- Mock profiles
- Mock projects
- Mock README files

### Test Database
Some tests require database connection:
- Use test database or SQLite for isolation
- Tests clean up after themselves
- Safe to run in development environment

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: python run_tests.py

    - name: Run coverage
      run: pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Code Quality Checks

### Linting

```bash
# Flake8 (code style)
flake8 .

# Black (code formatting)
black --check .

# MyPy (type checking)
mypy .

# Bandit (security)
bandit -r . -ll
```

### Auto-formatting

```bash
# Format all code
black .
```

## Writing New Tests

### Test Template

```python
"""Test module for [component]."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_feature_name():
    """Test [feature] functionality."""
    print("=" * 70)
    print("Test: [Feature Name]")
    print("=" * 70)

    try:
        # Setup
        print("[*] Setting up test...")

        # Execute
        print("[*] Testing feature...")
        result = do_something()

        # Assert
        assert result is not None, "Result should not be None"
        print("[OK] Test passed")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def run_all_tests():
    """Run all tests in this module."""
    tests = [
        test_feature_name,
        # Add more tests here
    ]

    passed = sum(1 for test in tests if test())
    failed = len(tests) - passed

    print(f"\n[OK] Passed: {passed}/{len(tests)}")
    print(f"[X] Failed: {failed}/{len(tests)}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

### Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Clean up created files/database records
3. **Mocking**: Mock external dependencies (APIs, databases when possible)
4. **Assertions**: Use descriptive assertion messages
5. **Documentation**: Add docstrings explaining what each test does
6. **Fast**: Unit tests should run in <1 second
7. **Deterministic**: Tests should always produce same result

## Common Issues

### Import Errors

**Problem:** `ModuleNotFoundError`
**Solution:** Add path setup at top of test file:
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### Database Connection Errors

**Problem:** Tests fail due to missing database
**Solution:**
- Configure test database in `.env`
- Or skip tests with `pytest -m "not requires_db"`

### Slow Tests

**Problem:** Test suite takes too long
**Solution:**
- Mark slow tests: `@pytest.mark.slow`
- Skip in CI: `pytest -m "not slow"`
- Mock external calls

## Test Metrics

### Performance Targets

| Operation | Target | Actual |
|-----------|--------|--------|
| Embedding (1 text) | <500ms | ~300ms |
| README parsing | <100ms | ~50ms |
| Filter 100 jobs | <200ms | ~150ms |
| CSV export 50 jobs | <150ms | ~80ms |
| Excel export 5 sheets | <1000ms | ~600ms |

### Success Criteria

- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Performance benchmarks within targets
- ✅ Code quality checks pass (flake8, black, mypy)
- ✅ No security issues (bandit)

## Support

For test-related issues:
1. Check test output for detailed error messages
2. Run individual test files to isolate issues
3. Verify dependencies are installed: `pip install -r requirements-dev.txt`
4. Check `.env` configuration for database/API keys
