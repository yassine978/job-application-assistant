"""CV parser to extract information from PDF resumes."""

from typing import Dict, List, Optional
import re
from pathlib import Path


class CVParser:
    """Parse CVs from PDF files to extract structured information."""

    def __init__(self):
        """Initialize CV parser."""
        self.skill_keywords = [
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
            'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
            # Frameworks/Libraries
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'spring', 'node.js',
            'express', 'next.js', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'opencv',
            # Databases
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
            'dynamodb', 'sqlite', 'oracle', 'mariadb',
            # Tools & Platforms
            'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'gitlab',
            'github', 'jira', 'confluence', 'slack', 'terraform', 'ansible',
            # Concepts
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
            'data analysis', 'web development', 'mobile development', 'devops', 'ci/cd',
            'agile', 'scrum', 'microservices', 'rest api', 'graphql', 'websockets'
        ]

    def initialize(self):
        """Initialize dependencies."""
        print("[OK] CV Parser initialized")

    def parse_pdf(self, pdf_path: Path) -> Dict:
        """Parse a PDF CV file and extract structured information.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with extracted profile data
        """
        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(pdf_path)

            # Parse sections
            profile_data = {
                'skills': self._extract_skills(text),
                'experience': self._extract_experience(text),
                'education': self._extract_education(text),
                'languages': self._extract_languages(text),
                'contact': self._extract_contact(text)
            }

            return profile_data

        except Exception as e:
            print(f"Error parsing CV: {e}")
            return self._empty_profile()

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract raw text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(pdf_path)
            text = ""

            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text

        except ImportError:
            print("PyPDF2 not installed. Attempting alternative method...")
            # Fallback to pdfplumber if available
            try:
                import pdfplumber

                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"

                return text

            except ImportError:
                raise ImportError("No PDF parsing library available. Install PyPDF2 or pdfplumber.")

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from CV text.

        Args:
            text: CV text

        Returns:
            List of extracted skills
        """
        text_lower = text.lower()
        found_skills = []

        # Find skills from keyword list
        for skill in self.skill_keywords:
            if skill in text_lower:
                # Capitalize properly
                found_skills.append(skill.title())

        # Look for skills section
        skills_match = re.search(
            r'(?:skills|competences|technologies|tech stack)[:\s]+(.*?)(?:\n\n|\n[A-Z])',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if skills_match:
            skills_section = skills_match.group(1)
            # Split by common delimiters
            additional_skills = re.split(r'[,•\|\n-]+', skills_section)
            for skill in additional_skills:
                skill = skill.strip()
                if skill and len(skill) > 2 and len(skill) < 30:
                    # Clean up and add if not already present
                    skill_clean = re.sub(r'[^\w\s+#.-]', '', skill)
                    if skill_clean and skill_clean not in found_skills:
                        found_skills.append(skill_clean)

        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)

        return unique_skills[:30]  # Limit to 30 most relevant

    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience from CV text.

        Args:
            text: CV text

        Returns:
            List of experience dictionaries
        """
        experiences = []

        # Look for experience section
        exp_patterns = [
            r'(?:EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT)(.*?)(?:EDUCATION|SKILLS|PROJECTS|$)',
            r'(?:Experience professionnelle|Expérience)(.*?)(?:Formation|Éducation|Compétences|$)'
        ]

        exp_section = ""
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                exp_section = match.group(1)
                break

        if not exp_section:
            return experiences

        # Split by common job entry patterns
        # Look for patterns like: "Job Title | Company | Date"
        job_entries = re.split(r'\n(?=\S.*?(?:\||@|at)\s*\S)', exp_section)

        for entry in job_entries:
            entry = entry.strip()
            if len(entry) < 20:  # Too short to be a real entry
                continue

            # Extract title and company
            # Pattern: "Title | Company" or "Title at Company"
            title_company_match = re.search(
                r'^([^|\n]+?)(?:\s*[\|@]\s*|\s+at\s+)([^|\n]+?)(?:\s*[\|]\s*|\n)',
                entry,
                re.IGNORECASE
            )

            if title_company_match:
                title = title_company_match.group(1).strip()
                company = title_company_match.group(2).strip()

                # Extract date/duration
                date_match = re.search(
                    r'(\d{4}|\w+\s+\d{4})\s*[-–—to]+\s*(\d{4}|\w+\s+\d{4}|present|current)',
                    entry,
                    re.IGNORECASE
                )
                duration = date_match.group(0) if date_match else ""

                # Extract description (rest of the entry)
                description = entry
                if title_company_match:
                    description = entry[title_company_match.end():].strip()
                # Clean up description
                description = re.sub(r'\n+', ' ', description)
                description = description[:500]  # Limit length

                experiences.append({
                    'title': title,
                    'company': company,
                    'duration': duration,
                    'description': description
                })

        return experiences[:10]  # Limit to 10 most recent

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education from CV text.

        Args:
            text: CV text

        Returns:
            List of education dictionaries
        """
        education_list = []

        # Look for education section
        edu_patterns = [
            r'(?:EDUCATION|ACADEMIC BACKGROUND|QUALIFICATIONS)(.*?)(?:EXPERIENCE|SKILLS|PROJECTS|$)',
            r'(?:Formation|Éducation)(.*?)(?:Expérience|Compétences|$)'
        ]

        edu_section = ""
        for pattern in edu_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                edu_section = match.group(1)
                break

        if not edu_section:
            return education_list

        # Split by entries
        edu_entries = re.split(r'\n(?=\S)', edu_section)

        for entry in edu_entries:
            entry = entry.strip()
            if len(entry) < 15:  # Too short
                continue

            # Look for degree patterns
            degree_match = re.search(
                r'(Bachelor|Master|PhD|Doctorate|Diploma|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|Engineering)(?:\s+(?:of|in|degree))?\s+([^\n]+)',
                entry,
                re.IGNORECASE
            )

            # Look for institution
            institution_match = re.search(
                r'(?:University|College|Institute|School|École|Université)\s+(?:of\s+)?([^\n,]+)',
                entry,
                re.IGNORECASE
            )

            # Look for year
            year_match = re.search(r'(19|20)\d{2}', entry)

            if degree_match or institution_match:
                degree = degree_match.group(0).strip() if degree_match else entry.split('\n')[0][:100]
                institution = institution_match.group(0).strip() if institution_match else "Unknown"
                year = int(year_match.group(0)) if year_match else None

                # Extract field of study
                field = ""
                if degree_match and len(degree_match.groups()) > 1:
                    field = degree_match.group(2).strip()

                education_list.append({
                    'degree': degree,
                    'institution': institution,
                    'year': year,
                    'field': field
                })

        return education_list[:5]  # Limit to 5 entries

    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from CV text.

        Args:
            text: CV text

        Returns:
            List of languages with proficiency
        """
        languages = []

        # Look for languages section
        lang_match = re.search(
            r'(?:LANGUAGES?|LANGUES?)[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if lang_match:
            lang_section = lang_match.group(1)

            # Common languages
            lang_patterns = [
                r'(English|French|Spanish|German|Italian|Portuguese|Chinese|Japanese|Arabic|Russian|Hindi)(?:\s*[:-]\s*|\s+\()?([A-Z][a-z]+)?',
            ]

            for pattern in lang_patterns:
                matches = re.finditer(pattern, lang_section, re.IGNORECASE)
                for match in matches:
                    lang = match.group(1).capitalize()
                    level = match.group(2).capitalize() if len(match.groups()) > 1 and match.group(2) else ""

                    if level:
                        languages.append(f"{lang} ({level})")
                    else:
                        languages.append(lang)

        # Remove duplicates
        languages = list(dict.fromkeys(languages))

        return languages[:10]  # Limit to 10 languages

    def _extract_contact(self, text: str) -> Dict:
        """Extract contact information from CV text.

        Args:
            text: CV text

        Returns:
            Dictionary with contact info
        """
        contact = {
            'email': None,
            'phone': None,
            'linkedin': None
        }

        # Extract email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            contact['email'] = email_match.group(0)

        # Extract phone
        phone_match = re.search(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,5}[-\s\.]?[0-9]{1,5}', text)
        if phone_match:
            contact['phone'] = phone_match.group(0)

        # Extract LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/([a-zA-Z0-9-]+)', text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin'] = f"https://linkedin.com/in/{linkedin_match.group(1)}"

        return contact

    def _empty_profile(self) -> Dict:
        """Return empty profile structure.

        Returns:
            Empty profile dictionary
        """
        return {
            'skills': [],
            'experience': [],
            'education': [],
            'languages': [],
            'contact': {'email': None, 'phone': None, 'linkedin': None}
        }


# Global instance
cv_parser = CVParser()
