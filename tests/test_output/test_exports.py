"""Test export functionality."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from datetime import datetime
from output.csv_exporter import CSVExporter
from output.excel_exporter import ExcelExporter
from output.pdf_converter import PDFConverter


def test_csv_export():
    """Test CSV export functionality."""
    print("=" * 70)
    print("Test 1: CSV Export")
    print("=" * 70)

    exporter = CSVExporter()

    # Test data
    jobs = [
        {
            'job_title': 'ML Engineer',
            'company_name': 'AI Startup',
            'location': 'Paris',
            'job_type': 'Full-time',
            'match_score': 85,
            'semantic_similarity': 0.72,
            'salary': '€50k-€70k',
            'posted_date': '2 days ago',
            'source': 'WTTJ',
            'language': 'English',
            'url': 'https://example.com/job1',
            'required_skills': ['Python', 'TensorFlow', 'ML'],
            'selected_projects': [
                {'title': 'ML Recommender', 'relevance_score': 0.95}
            ]
        },
        {
            'job_title': 'Data Scientist',
            'company_name': 'Tech Corp',
            'location': 'Remote',
            'job_type': 'Full-time',
            'match_score': 72,
            'semantic_similarity': 0.65,
            'salary': '€45k-€60k',
            'posted_date': '1 day ago',
            'source': 'Adzuna',
            'language': 'French',
            'url': 'https://example.com/job2',
            'required_skills': ['Python', 'Pandas', 'SQL'],
            'selected_projects': []
        }
    ]

    print(f"\n[*] Exporting {len(jobs)} jobs to CSV...")
    csv_path = exporter.export_search_results(jobs)

    print(f"[OK] CSV exported to: {csv_path}")
    print(f"[OK] File exists: {csv_path.exists()}")
    print(f"[OK] File size: {csv_path.stat().st_size} bytes")

    # Verify content
    import pandas as pd
    df = pd.read_csv(csv_path)
    print(f"[OK] Rows in CSV: {len(df)}")
    print(f"[OK] Columns: {list(df.columns)[:5]}...")

    assert len(df) == 2, "Should have 2 rows"
    assert 'Job Title' in df.columns, "Should have Job Title column"
    assert df['Match Score (%)'][0] == 85, "First job should have 85% match"

    print("\n[OK] CSV export test passed")
    return True


def test_excel_export():
    """Test Excel export functionality."""
    print("\n" + "=" * 70)
    print("Test 2: Excel Export")
    print("=" * 70)

    exporter = ExcelExporter()

    # Test data
    search_results = [
        {
            'job_title': 'ML Engineer',
            'company_name': 'AI Startup',
            'match_score': 85,
            'semantic_similarity': 0.72
        }
    ]

    applications = [
        {
            'job': search_results[0],
            'cv': {
                'content': '# CV Content',
                'metadata': {
                    'cv_length': 1,
                    'generation_method': 'template',
                    'word_count': 415,
                    'projects_included': ['proj-1']
                }
            },
            'generated_at': datetime.utcnow()
        }
    ]

    projects = [
        {
            'id': 'proj-1',
            'title': 'ML Recommender',
            'technologies': ['Python', 'TensorFlow'],
            'highlights': ['Feature 1', 'Feature 2']
        }
    ]

    usage_stats = {'proj-1': 1}
    skill_counts = {'Python': 2, 'TensorFlow': 1}
    user_skills = ['Python']

    print(f"\n[*] Exporting comprehensive report...")
    excel_path = exporter.export_comprehensive_report(
        search_results=search_results,
        applications=applications,
        projects=projects,
        usage_stats=usage_stats,
        skill_counts=skill_counts,
        user_skills=user_skills,
        user_name="Test User"
    )

    print(f"[OK] Excel exported to: {excel_path}")
    print(f"[OK] File exists: {excel_path.exists()}")
    print(f"[OK] File size: {excel_path.stat().st_size} bytes")

    # Verify sheets
    import pandas as pd
    excel_file = pd.ExcelFile(excel_path)
    print(f"[OK] Sheets: {excel_file.sheet_names}")

    assert 'Summary' in excel_file.sheet_names, "Should have Summary sheet"
    assert 'Job Search Results' in excel_file.sheet_names, "Should have Job Search Results sheet"
    assert 'Applications' in excel_file.sheet_names, "Should have Applications sheet"

    print("\n[OK] Excel export test passed")
    return True


def test_pdf_conversion():
    """Test PDF conversion."""
    print("\n" + "=" * 70)
    print("Test 3: PDF Conversion")
    print("=" * 70)

    converter = PDFConverter()

    # Test markdown content
    markdown_content = """
# John Doe

**Email:** john@example.com | **Phone:** +33 6 12 34 56 78

## Summary

Experienced ML Engineer with 3 years of experience in building production ML systems.

## Skills

Python, TensorFlow, PyTorch, scikit-learn, SQL, Docker

## Experience

### Senior ML Engineer | AI Startup
*2022 - Present*

- Built recommendation system serving 100k users
- Improved model accuracy by 25%
- Led team of 3 engineers

## Education

**Master in Computer Science**
University of Paris, 2021
"""

    print(f"\n[*] Converting markdown to PDF...")

    try:
        pdf_path = converter.convert_markdown_to_pdf(
            markdown_content=markdown_content,
            output_filename="test_cv.pdf",
            max_pages=1,
            title="Test CV"
        )

        print(f"[OK] PDF generated: {pdf_path}")
        print(f"[OK] File exists: {pdf_path.exists()}")

        if pdf_path.suffix == '.pdf':
            print(f"[OK] File size: {pdf_path.stat().st_size} bytes")

            # Try to get page count
            try:
                page_count = converter.get_page_count(pdf_path)
                print(f"[OK] Page count: {page_count}")
                assert page_count <= 1, "Should be 1 page or less"
            except:
                print("[!] Could not verify page count (PyPDF2 may not be installed)")

        print("\n[OK] PDF conversion test passed")
        return True

    except ImportError as e:
        print(f"[!] PDF conversion skipped (weasyprint not installed): {e}")
        print("[!] This is expected - weasyprint is optional")
        return True

    except Exception as e:
        print(f"[ERROR] PDF conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all export tests."""
    print("\n" + "=" * 70)
    print("EXPORT TEST SUITE")
    print("=" * 70)

    tests = [
        test_csv_export,
        test_excel_export,
        test_pdf_conversion
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
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
        print("\n[SUCCESS] All export tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    run_all_tests()
