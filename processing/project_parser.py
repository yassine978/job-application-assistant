"""Parse README.md files to extract project information."""

import re
from typing import Dict, List, Optional
import mistune
from bs4 import BeautifulSoup


class ProjectParser:
    """Parse README.md files and extract structured project information."""

    def __init__(self):
        """Initialize the parser."""
        self.markdown_parser = mistune.create_markdown()

    def parse_readme(self, readme_content: str) -> Dict:
        """Parse README.md and extract structured info.

        Args:
            readme_content: Raw markdown content from README file

        Returns:
            Dictionary with extracted project information:
            {
                'title': str,
                'description': str,
                'technologies': List[str],
                'highlights': List[str]
            }
        """
        if not readme_content or not readme_content.strip():
            return {
                'title': '',
                'description': '',
                'technologies': [],
                'highlights': []
            }

        # Convert markdown to HTML for easier parsing
        html_content = self.markdown_parser(readme_content)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract components
        title = self._extract_title(soup, readme_content)
        description = self._extract_description(soup, readme_content)
        technologies = self._extract_technologies(readme_content, soup)
        highlights = self._extract_highlights(soup, readme_content)

        return {
            'title': title,
            'description': description,
            'technologies': technologies,
            'highlights': highlights
        }

    def _extract_title(self, soup: BeautifulSoup, raw_content: str) -> str:
        """Extract project title from README.

        Looks for:
        1. First H1 heading
        2. First H2 heading if no H1
        3. First line if no headings

        Args:
            soup: BeautifulSoup parsed HTML
            raw_content: Raw markdown content

        Returns:
            Extracted title
        """
        # Try H1 first
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text().strip()
            # Remove common badges/emojis
            title = re.sub(r'\[.*?\]\(.*?\)', '', title)  # Remove markdown links
            title = re.sub(r'[📦🚀🎯💡🔥⭐✨]', '', title)  # Remove emojis
            return title.strip()

        # Try H2
        h2 = soup.find('h2')
        if h2:
            title = h2.get_text().strip()
            title = re.sub(r'\[.*?\]\(.*?\)', '', title)
            title = re.sub(r'[📦🚀🎯💡🔥⭐✨]', '', title)
            return title.strip()

        # Fallback to first non-empty line
        lines = raw_content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('['):
                # Clean it up
                line = re.sub(r'\[.*?\]\(.*?\)', '', line)
                line = re.sub(r'[📦🚀🎯💡🔥⭐✨]', '', line)
                if line.strip():
                    return line.strip()

        return "Untitled Project"

    def _extract_description(self, soup: BeautifulSoup, raw_content: str) -> str:
        """Extract project description.

        Looks for:
        1. Text after title and before first H2
        2. First paragraph after title
        3. Section labeled "Description" or "About"

        Args:
            soup: BeautifulSoup parsed HTML
            raw_content: Raw markdown content

        Returns:
            Extracted description
        """
        # Look for "About" or "Description" sections
        for heading in soup.find_all(['h2', 'h3']):
            heading_text = heading.get_text().lower().strip()
            if any(keyword in heading_text for keyword in ['about', 'description', 'overview', 'summary']):
                # Get the next paragraph or list
                next_elem = heading.find_next(['p', 'ul'])
                if next_elem:
                    text = next_elem.get_text().strip()
                    # Limit to reasonable length
                    return text[:500] if len(text) > 500 else text

        # Try to get first paragraph after H1
        h1 = soup.find('h1')
        if h1:
            next_p = h1.find_next('p')
            if next_p:
                text = next_p.get_text().strip()
                # Skip if it looks like a badge line
                if not re.search(r'^\[.*?\].*?\[.*?\]', text):
                    return text[:500] if len(text) > 500 else text

        # Fallback: get all paragraphs and take the first substantial one
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            # Skip short or badge-heavy paragraphs
            if len(text) > 50 and not re.search(r'^\[.*?\].*?\[.*?\]', text):
                return text[:500] if len(text) > 500 else text

        return ""

    def _extract_technologies(self, raw_content: str, soup: BeautifulSoup) -> List[str]:
        """Extract technologies/tech stack from README.

        Looks for:
        1. Badges (shields.io, etc.)
        2. "Built with", "Technologies", "Tech Stack" sections
        3. Code blocks with language names
        4. Common technology keywords

        Args:
            raw_content: Raw markdown content
            soup: BeautifulSoup parsed HTML

        Returns:
            List of technology names
        """
        technologies = set()

        # 1. Extract from badges
        badge_matches = re.findall(r'badge/([^-]+)-', raw_content, re.IGNORECASE)
        for tech in badge_matches:
            # Clean up badge text
            tech = tech.replace('%20', ' ').replace('_', ' ')
            if len(tech) > 2 and len(tech) < 30:  # Reasonable tech name length
                technologies.add(tech.title())

        # 2. Look for technology sections
        tech_keywords = ['technologies', 'tech stack', 'built with', 'stack', 'tools']
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower().strip()
            if any(keyword in heading_text for keyword in tech_keywords):
                # Get the next list or paragraph
                next_list = heading.find_next('ul')
                if next_list:
                    items = next_list.find_all('li')
                    for item in items:
                        tech_text = item.get_text().strip()
                        # Extract tech name (usually before first dash or parenthesis)
                        tech_name = re.split(r'[-–—(]', tech_text)[0].strip()
                        # Remove markdown links
                        tech_name = re.sub(r'\[([^\]]+)\].*', r'\1', tech_name)
                        if len(tech_name) > 2 and len(tech_name) < 30:
                            technologies.add(tech_name)

        # 3. Extract from common patterns in text
        common_techs = [
            'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Svelte', 'Next.js', 'Nuxt',
            'Node.js', 'Express', 'Django', 'Flask', 'FastAPI', 'Spring', 'Rails',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
            'TensorFlow', 'PyTorch', 'scikit-learn', 'Keras',
            'Git', 'GitHub', 'GitLab', 'CI/CD',
            'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'Sass',
            'GraphQL', 'REST', 'API',
            'Webpack', 'Vite', 'Babel',
            'Jest', 'Pytest', 'Mocha', 'Cypress',
            'Pandas', 'NumPy', 'Matplotlib',
            'Stripe', 'Auth0', 'Firebase'
        ]

        content_lower = raw_content.lower()
        for tech in common_techs:
            # Use word boundary to avoid partial matches
            pattern = r'\b' + re.escape(tech.lower()) + r'\b'
            if re.search(pattern, content_lower):
                technologies.add(tech)

        # Clean up and return sorted list
        technologies = [t for t in technologies if t and len(t) > 1]
        return sorted(list(technologies))

    def _extract_highlights(self, soup: BeautifulSoup, raw_content: str) -> List[str]:
        """Extract project highlights/achievements/features.

        Looks for:
        1. "Features", "Highlights", "Key Features" sections
        2. Bullet points with achievements
        3. Numbers/metrics (e.g., "1000 users", "50% improvement")

        Args:
            soup: BeautifulSoup parsed HTML
            raw_content: Raw markdown content

        Returns:
            List of highlight strings
        """
        highlights = []

        # Look for relevant sections
        highlight_keywords = ['features', 'highlights', 'key features', 'achievements',
                             'capabilities', 'what it does']

        for heading in soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower().strip()
            if any(keyword in heading_text for keyword in highlight_keywords):
                # Get the next list
                next_list = heading.find_next('ul')
                if next_list:
                    items = next_list.find_all('li')
                    for item in items:
                        text = item.get_text().strip()
                        # Clean up markdown
                        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
                        if text and len(text) > 10:  # Reasonable highlight length
                            highlights.append(text)

                        # Stop at 10 highlights from this section
                        if len(highlights) >= 10:
                            break

        # If no highlights found in sections, look for lists with metrics/achievements
        if len(highlights) < 3:
            all_lists = soup.find_all('ul')
            for ul in all_lists:
                items = ul.find_all('li')
                for item in items:
                    text = item.get_text().strip()
                    # Look for items with numbers/percentages (likely metrics)
                    if re.search(r'\d+[%kK]|\d+\s*(users|customers|downloads|stars)', text):
                        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
                        if text and len(text) > 10:
                            highlights.append(text)

                    if len(highlights) >= 10:
                        break

                if len(highlights) >= 10:
                    break

        # Limit to top 10 highlights
        return highlights[:10]

    def parse_readme_file(self, file_path: str) -> Dict:
        """Parse README file from path.

        Args:
            file_path: Path to README.md file

        Returns:
            Parsed project information dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_readme(content)
        except FileNotFoundError:
            print(f"Error: README file not found at {file_path}")
            return {
                'title': '',
                'description': '',
                'technologies': [],
                'highlights': []
            }
        except Exception as e:
            print(f"Error parsing README file: {e}")
            return {
                'title': '',
                'description': '',
                'technologies': [],
                'highlights': []
            }

    def validate_parsed_data(self, parsed_data: Dict) -> bool:
        """Validate that parsed data has minimum required information.

        Args:
            parsed_data: Parsed project dictionary

        Returns:
            True if valid, False otherwise
        """
        # Check required fields exist
        required_fields = ['title', 'description', 'technologies', 'highlights']
        if not all(field in parsed_data for field in required_fields):
            return False

        # Check that at least title exists
        if not parsed_data['title'] or parsed_data['title'] == 'Untitled Project':
            return False

        # Should have some content
        has_content = (
            len(parsed_data['description']) > 20 or
            len(parsed_data['technologies']) > 0 or
            len(parsed_data['highlights']) > 0
        )

        return has_content


# Global parser instance
project_parser = ProjectParser()
