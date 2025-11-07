"""Test project parser functionality."""

from processing.project_parser import ProjectParser, project_parser


# Sample README contents for testing
SAMPLE_README_1 = """
# E-Commerce Recommendation System

A full-stack machine learning recommendation system built with modern technologies.

## About

This project implements a collaborative filtering recommendation engine that serves
personalized product recommendations to users. Built for scalability and performance.

## Technologies

- Python
- TensorFlow
- Flask
- PostgreSQL
- Redis
- Docker

## Features

- Real-time recommendations using ML models
- Handles 10,000+ concurrent users
- RESTful API with GraphQL support
- Improved CTR by 35%
- Deployed on AWS with auto-scaling
- 99.9% uptime SLA

## Installation

```bash
pip install -r requirements.txt
```
"""

SAMPLE_README_2 = """
# 🚀 Task Management App

![Python](https://img.shields.io/badge/Python-3.9-blue)
![React](https://img.shields.io/badge/React-18-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern, responsive task management application with real-time collaboration.

## Key Features

- Real-time task updates
- Mobile responsive design
- Secure authentication with JWT
- Analytics dashboard
- Dark mode support

## Built With

- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Deployment**: Docker, Kubernetes, AWS
"""

SAMPLE_README_3 = """
# Project Title

Simple project description here.

Some more text about the project.
"""

SAMPLE_README_MINIMAL = """
# Minimal Project

Just a title and nothing else.
"""

SAMPLE_README_NO_TITLE = """
This is a README without a proper title heading.

It has some content but no H1 or H2.

Technologies: Python, Django, React
"""


def test_parse_comprehensive_readme():
    """Test parsing a comprehensive README with all sections."""
    print("=" * 60)
    print("Test 1: Comprehensive README Parsing")
    print("=" * 60)

    parser = ProjectParser()
    result = parser.parse_readme(SAMPLE_README_1)

    print(f"\n[*] Title: {result['title']}")
    print(f"[*] Description ({len(result['description'])} chars):")
    print(f"   {result['description'][:100]}...")
    print(f"[*] Technologies ({len(result['technologies'])}): {result['technologies'][:5]}")
    print(f"[*] Highlights ({len(result['highlights'])}): {result['highlights'][:3]}")

    # Assertions
    assert result['title'] == "E-Commerce Recommendation System", f"Expected title, got: {result['title']}"
    assert len(result['description']) > 50, "Description should be substantial"
    assert 'Python' in result['technologies'], "Should detect Python"
    assert 'TensorFlow' in result['technologies'], "Should detect TensorFlow"
    assert len(result['highlights']) > 0, "Should extract highlights"

    print("\n[OK] Comprehensive README parsing works!")
    return True


def test_parse_with_badges():
    """Test parsing README with badges and emojis."""
    print("\n" + "=" * 60)
    print("Test 2: README with Badges and Emojis")
    print("=" * 60)

    parser = ProjectParser()
    result = parser.parse_readme(SAMPLE_README_2)

    print(f"\n[*] Title: {result['title']}")
    print(f"[*] Description: {result['description'][:100]}...")
    print(f"[*] Technologies: {result['technologies'][:8]}")
    print(f"[*] Highlights: {result['highlights'][:3]}")

    # Assertions
    assert "Task Management App" in result['title'], f"Title should be clean, got: {result['title']}"
    assert '🚀' not in result['title'], "Should remove emojis from title"
    assert 'React' in result['technologies'], "Should extract React from badge"
    assert 'Python' in result['technologies'], "Should extract Python from badge"
    assert 'TypeScript' in result['technologies'], "Should extract TypeScript"
    assert 'FastAPI' in result['technologies'], "Should extract FastAPI"

    print("\n[OK] Badge and emoji parsing works!")
    return True


def test_parse_simple_readme():
    """Test parsing a simple README."""
    print("\n" + "=" * 60)
    print("Test 3: Simple README Parsing")
    print("=" * 60)

    parser = ProjectParser()
    result = parser.parse_readme(SAMPLE_README_3)

    print(f"\n[*] Title: {result['title']}")
    print(f"[*] Description: {result['description']}")
    print(f"[*] Technologies: {result['technologies']}")
    print(f"[*] Highlights: {result['highlights']}")

    # Assertions
    assert result['title'] == "Project Title", "Should extract basic title"
    assert len(result['description']) > 0, "Should have some description"

    print("\n[OK] Simple README parsing works!")
    return True


def test_parse_minimal_readme():
    """Test parsing minimal README."""
    print("\n" + "=" * 60)
    print("Test 4: Minimal README Parsing")
    print("=" * 60)

    parser = ProjectParser()
    result = parser.parse_readme(SAMPLE_README_MINIMAL)

    print(f"\n[*] Title: {result['title']}")
    print(f"[*] Description: '{result['description']}'")
    print(f"[*] Technologies: {result['technologies']}")
    print(f"[*] Highlights: {result['highlights']}")

    # Assertions
    assert result['title'] == "Minimal Project", "Should extract title"
    assert isinstance(result['technologies'], list), "Should return empty list"
    assert isinstance(result['highlights'], list), "Should return empty list"

    print("\n[OK] Minimal README parsing works!")
    return True


def test_parse_no_title_readme():
    """Test parsing README without proper headings."""
    print("\n" + "=" * 60)
    print("Test 5: README Without Title Heading")
    print("=" * 60)

    parser = ProjectParser()
    result = parser.parse_readme(SAMPLE_README_NO_TITLE)

    print(f"\n[*] Title: {result['title']}")
    print(f"[*] Description: {result['description'][:50] if result['description'] else 'None'}...")
    print(f"[*] Technologies: {result['technologies']}")
    print(f"[*] Highlights: {result['highlights']}")

    # Should still extract something
    assert result['title'] != '', "Should extract fallback title"
    assert 'Python' in result['technologies'], "Should detect Python in text"
    assert 'Django' in result['technologies'], "Should detect Django in text"
    assert 'React' in result['technologies'], "Should detect React in text"

    print("\n[OK] No-title README parsing works!")
    return True


def test_empty_readme():
    """Test parsing empty README."""
    print("\n" + "=" * 60)
    print("Test 6: Empty README")
    print("=" * 60)

    parser = ProjectParser()
    result = parser.parse_readme("")

    print(f"\n[*] Result: {result}")

    # Should return empty structure
    assert result['title'] == '', "Should return empty title"
    assert result['description'] == '', "Should return empty description"
    assert result['technologies'] == [], "Should return empty list"
    assert result['highlights'] == [], "Should return empty list"

    print("\n[OK] Empty README handling works!")
    return True


def test_validate_parsed_data():
    """Test validation of parsed data."""
    print("\n" + "=" * 60)
    print("Test 7: Data Validation")
    print("=" * 60)

    parser = ProjectParser()

    # Valid data
    valid_data = {
        'title': 'My Project',
        'description': 'This is a good description with enough content',
        'technologies': ['Python', 'React'],
        'highlights': ['Feature 1', 'Feature 2']
    }

    assert parser.validate_parsed_data(valid_data) == True, "Should validate good data"
    print("[OK] Valid data accepted")

    # Invalid - no title
    invalid_data_1 = {
        'title': '',
        'description': 'Good description',
        'technologies': ['Python'],
        'highlights': []
    }

    assert parser.validate_parsed_data(invalid_data_1) == False, "Should reject empty title"
    print("[OK] Empty title rejected")

    # Invalid - no content
    invalid_data_2 = {
        'title': 'Title',
        'description': '',
        'technologies': [],
        'highlights': []
    }

    assert parser.validate_parsed_data(invalid_data_2) == False, "Should reject no content"
    print("[OK] No content rejected")

    print("\n[OK] Data validation works!")
    return True


def test_technology_extraction():
    """Test technology extraction from various formats."""
    print("\n" + "=" * 60)
    print("Test 8: Technology Extraction")
    print("=" * 60)

    readme_with_techs = """
# Project

Built with Python, TensorFlow, and React.

## Tech Stack

- Node.js - Backend runtime
- Express - Web framework
- MongoDB - Database
- Docker - Containerization

Uses AWS for deployment and PostgreSQL for data storage.
"""

    parser = ProjectParser()
    result = parser.parse_readme(readme_with_techs)

    print(f"\n[*] Extracted technologies: {result['technologies']}")

    expected_techs = ['Python', 'TensorFlow', 'React', 'Node.js',
                      'Express', 'MongoDB', 'Docker', 'AWS', 'PostgreSQL']

    for tech in expected_techs:
        assert tech in result['technologies'], f"Should extract {tech}"
        print(f"   [OK] Found: {tech}")

    print("\n[OK] Technology extraction works!")
    return True


def test_highlight_extraction():
    """Test highlight extraction from features section."""
    print("\n" + "=" * 60)
    print("Test 9: Highlight Extraction")
    print("=" * 60)

    readme_with_highlights = """
# Project

## Features

- Supports 1000+ concurrent users
- 50% faster than competitors
- Mobile responsive design
- Real-time updates
- Advanced analytics
"""

    parser = ProjectParser()
    result = parser.parse_readme(readme_with_highlights)

    print(f"\n[*] Extracted highlights:")
    for highlight in result['highlights']:
        print(f"   - {highlight}")

    assert len(result['highlights']) > 0, "Should extract highlights"
    assert any('1000' in h for h in result['highlights']), "Should extract metrics"

    print("\n[OK] Highlight extraction works!")
    return True


def test_global_parser_instance():
    """Test the global parser instance."""
    print("\n" + "=" * 60)
    print("Test 10: Global Parser Instance")
    print("=" * 60)

    result = project_parser.parse_readme(SAMPLE_README_1)

    print(f"\n[*] Title: {result['title']}")
    print(f"[*] Technologies: {len(result['technologies'])} found")

    assert result['title'] == "E-Commerce Recommendation System"
    print("\n[OK] Global parser instance works!")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("PROJECT PARSER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        test_parse_comprehensive_readme,
        test_parse_with_badges,
        test_parse_simple_readme,
        test_parse_minimal_readme,
        test_parse_no_title_readme,
        test_empty_readme,
        test_validate_parsed_data,
        test_technology_extraction,
        test_highlight_extraction,
        test_global_parser_instance
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"\n[X] Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[X] Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"[OK] Passed: {passed}/{len(tests)}")
    print(f"[X] Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n[SUCCESS] All tests passed! Project Parser is ready to use.")
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please review.")

    return failed == 0


if __name__ == "__main__":
    run_all_tests()
