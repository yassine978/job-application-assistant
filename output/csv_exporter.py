"""CSV export functionality for job applications."""

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class CSVExporter:
    """Export job applications and search results to CSV format."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize CSV exporter.

        Args:
            output_dir: Directory to save CSV files
        """
        if output_dir is None:
            from config import GENERATED_DOCS_DIR
            output_dir = GENERATED_DOCS_DIR / "exports"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_search_results(
        self,
        jobs: List[Dict],
        filename: Optional[str] = None
    ) -> Path:
        """Export job search results to CSV.

        Args:
            jobs: List of job dictionaries with match scores
            filename: Output filename (auto-generated if None)

        Returns:
            Path to generated CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_search_results_{timestamp}.csv"

        # Prepare data
        rows = []
        for i, job in enumerate(jobs):
            row = {
                'Rank': i + 1,
                'Job Title': job.get('job_title', 'N/A'),
                'Company': job.get('company_name', 'N/A'),
                'Location': job.get('location', 'N/A'),
                'Job Type': job.get('job_type', 'N/A'),
                'Match Score (%)': job.get('match_score', 0),
                'Semantic Similarity (%)': round(job.get('semantic_similarity', 0) * 100, 1),
                'Salary': job.get('salary', 'N/A'),
                'Posted Date': job.get('posted_date', 'N/A'),
                'Source': job.get('source', 'N/A'),
                'Language': job.get('language', 'N/A'),
                'URL': job.get('url', 'N/A'),
                'Required Skills': ', '.join(job.get('required_skills', [])),
                'Projects Matched': len(job.get('selected_projects', [])),
                'Top Project': job.get('selected_projects', [{}])[0].get('title', 'N/A') if job.get('selected_projects') else 'N/A',
                'Top Project Relevance (%)': round(job.get('selected_projects', [{}])[0].get('relevance_score', 0) * 100, 1) if job.get('selected_projects') else 0,
            }
            rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Save to CSV
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        return output_path

    def export_applications(
        self,
        applications: List[Dict],
        filename: Optional[str] = None
    ) -> Path:
        """Export generated applications to CSV.

        Args:
            applications: List of application dictionaries
            filename: Output filename (auto-generated if None)

        Returns:
            Path to generated CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"applications_{timestamp}.csv"

        # Prepare data
        rows = []
        for i, app in enumerate(applications):
            job = app.get('job', {})
            cv = app.get('cv', {})
            metadata = cv.get('metadata', {})

            row = {
                'Application #': i + 1,
                'Job Title': job.get('job_title', 'N/A'),
                'Company': job.get('company_name', 'N/A'),
                'Location': job.get('location', 'N/A'),
                'Match Score (%)': job.get('match_score', 0),
                'CV Length (pages)': metadata.get('cv_length', 'N/A'),
                'Generation Method': metadata.get('generation_method', 'N/A'),
                'Word Count': metadata.get('word_count', 'N/A'),
                'Projects Included': len(metadata.get('projects_included', [])),
                'Generated At': app.get('generated_at', 'N/A'),
                'Job URL': job.get('url', 'N/A'),
                'Status': 'Generated',  # Placeholder for future tracking
            }
            rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Save to CSV
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        return output_path

    def export_projects_performance(
        self,
        projects: List[Dict],
        usage_stats: Dict[str, int],
        filename: Optional[str] = None
    ) -> Path:
        """Export project performance data to CSV.

        Args:
            projects: List of project dictionaries
            usage_stats: Dictionary mapping project IDs to usage counts
            filename: Output filename (auto-generated if None)

        Returns:
            Path to generated CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"project_performance_{timestamp}.csv"

        # Prepare data
        rows = []
        for project in projects:
            project_id = str(project.get('id', ''))
            usage_count = usage_stats.get(project_id, 0)

            row = {
                'Project Title': project.get('title', 'N/A'),
                'Technologies': ', '.join(project.get('technologies', [])),
                'Times Used': usage_count,
                'GitHub URL': project.get('github_url', 'N/A'),
                'Demo URL': project.get('demo_url', 'N/A'),
                'Highlights': ' | '.join(project.get('highlights', [])[:3]),
            }
            rows.append(row)

        # Create DataFrame and sort by usage
        df = pd.DataFrame(rows)
        df = df.sort_values('Times Used', ascending=False)

        # Save to CSV
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        return output_path

    def export_skills_gap_analysis(
        self,
        skill_counts: Dict[str, int],
        user_skills: List[str],
        total_jobs: int,
        filename: Optional[str] = None
    ) -> Path:
        """Export skills gap analysis to CSV.

        Args:
            skill_counts: Dictionary mapping skills to job counts
            user_skills: List of user's current skills
            total_jobs: Total number of jobs analyzed
            filename: Output filename (auto-generated if None)

        Returns:
            Path to generated CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"skills_gap_analysis_{timestamp}.csv"

        # Prepare data
        user_skills_lower = set(s.lower() for s in user_skills)
        rows = []

        for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True):
            has_skill = skill.lower() in user_skills_lower
            percentage = (count / total_jobs * 100) if total_jobs > 0 else 0

            row = {
                'Skill': skill,
                'Jobs Requiring': count,
                'Percentage of Jobs': round(percentage, 1),
                'You Have It': 'Yes' if has_skill else 'No',
                'Priority': 'High' if not has_skill and percentage >= 50 else 'Medium' if not has_skill and percentage >= 25 else 'Low'
            }
            rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Save to CSV
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        return output_path

    def export_all(
        self,
        search_results: List[Dict],
        applications: List[Dict],
        projects: List[Dict],
        usage_stats: Dict[str, int],
        skill_counts: Dict[str, int],
        user_skills: List[str],
        base_filename: Optional[str] = None
    ) -> Dict[str, Path]:
        """Export all data to separate CSV files.

        Args:
            search_results: Job search results
            applications: Generated applications
            projects: User projects
            usage_stats: Project usage statistics
            skill_counts: Skill frequency counts
            user_skills: User's current skills
            base_filename: Base name for files (timestamp used if None)

        Returns:
            Dictionary mapping export type to file path
        """
        if not base_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"export_{timestamp}"

        exports = {}

        # Export search results
        if search_results:
            exports['search_results'] = self.export_search_results(
                search_results,
                f"{base_filename}_search_results.csv"
            )

        # Export applications
        if applications:
            exports['applications'] = self.export_applications(
                applications,
                f"{base_filename}_applications.csv"
            )

        # Export project performance
        if projects:
            exports['projects'] = self.export_projects_performance(
                projects,
                usage_stats,
                f"{base_filename}_project_performance.csv"
            )

        # Export skills gap
        if skill_counts:
            total_jobs = len(search_results) if search_results else 0
            exports['skills'] = self.export_skills_gap_analysis(
                skill_counts,
                user_skills,
                total_jobs,
                f"{base_filename}_skills_gap.csv"
            )

        return exports


# Global exporter instance
csv_exporter = CSVExporter()
