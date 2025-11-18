"""Page length optimization for CV generation."""

from typing import Dict, List


class PageOptimizer:
    """Optimize CV content to fit within page limits."""

    # Word count targets for different page lengths
    WORD_LIMITS = {
        1: {
            'contact': 30,
            'summary': 50,
            'skills': 40,
            'experience': 150,
            'projects': 100,
            'education': 30,
            'languages': 15,
            'total': 415
        },
        2: {
            'contact': 40,
            'summary': 80,
            'skills': 60,
            'experience': 250,
            'projects': 200,
            'education': 60,
            'languages': 25,
            'total': 715
        }
    }

    # Priority weights for content sections
    PRIORITY_WEIGHTS = {
        'contact': 1.00,
        'summary': 0.95,
        'experience': 0.90,
        'skills': 0.85,
        'projects': 0.80,
        'education': 0.75,
        'languages': 0.70
    }

    def __init__(self):
        """Initialize page optimizer."""
        pass

    def optimize_content(
        self,
        content: Dict,
        target_pages: int = 1,
        include_projects: bool = True
    ) -> Dict:
        """Optimize content to fit target page count.

        Args:
            content: Dictionary with section content
            target_pages: Target number of pages (1 or 2)
            include_projects: Whether to include projects section

        Returns:
            Optimized content dictionary
        """
        if target_pages not in [1, 2]:
            target_pages = 1

        print(f"\n[PAGE OPTIMIZER] Optimizing for {target_pages} page(s)")

        limits = self.WORD_LIMITS[target_pages]

        optimized = {}

        # Optimize each section
        optimized['contact'] = self._optimize_contact(
            content.get('contact', {}),
            limits['contact']
        )

        optimized['summary'] = self._optimize_summary(
            content.get('summary', ''),
            limits['summary']
        )

        optimized['skills'] = self._optimize_skills(
            content.get('skills', []),
            limits['skills'],
            target_pages
        )

        optimized['experience'] = self._optimize_experience(
            content.get('experience', []),
            limits['experience'],
            target_pages
        )

        if include_projects:
            optimized['projects'] = self._optimize_projects(
                content.get('projects', []),
                limits['projects'],
                target_pages
            )
        else:
            optimized['projects'] = []

        optimized['education'] = self._optimize_education(
            content.get('education', []),
            limits['education'],
            target_pages
        )

        optimized['languages'] = self._optimize_languages(
            content.get('languages', []),
            limits['languages']
        )

        # Calculate total word count
        total_words = self._count_total_words(optimized)
        print(f"  Total words: {total_words}/{limits['total']}")

        # If still over limit, apply aggressive optimization
        if total_words > limits['total']:
            print(f"  Over limit, applying aggressive optimization...")
            optimized = self._aggressive_optimize(optimized, limits, target_pages)
            total_words = self._count_total_words(optimized)
            print(f"  After optimization: {total_words} words")

        return optimized

    def _optimize_contact(self, contact: Dict, word_limit: int) -> Dict:
        """Optimize contact section.

        Args:
            contact: Contact information
            word_limit: Maximum words

        Returns:
            Optimized contact
        """
        # Contact info is always compact, just format nicely
        return {
            'name': contact.get('name', ''),
            'email': contact.get('email', ''),
            'phone': contact.get('phone', ''),
            'location': contact.get('location', ''),
            'linkedin': contact.get('linkedin', '')
        }

    def _optimize_summary(self, summary: str, word_limit: int) -> str:
        """Optimize summary/objective.

        Args:
            summary: Summary text
            word_limit: Maximum words

        Returns:
            Optimized summary
        """
        if not summary:
            return ''

        words = summary.split()
        if len(words) <= word_limit:
            return summary

        # Truncate to word limit
        return ' '.join(words[:word_limit]) + '...'

    def _optimize_skills(self, skills: List[str], word_limit: int, pages: int) -> List[str]:
        """Optimize skills list.

        Args:
            skills: List of skills
            word_limit: Maximum words
            pages: Number of pages

        Returns:
            Optimized skills list
        """
        if not skills:
            return []

        # Determine how many skills to show
        max_skills = 10 if pages == 1 else 15

        return skills[:max_skills]

    def _optimize_experience(
        self,
        experience: List[Dict],
        word_limit: int,
        pages: int
    ) -> List[Dict]:
        """Optimize experience section.

        Args:
            experience: List of experience entries
            word_limit: Maximum words
            pages: Number of pages

        Returns:
            Optimized experience list
        """
        if not experience:
            return []

        # Limit number of roles
        max_roles = 3 if pages == 1 else 5
        limited_exp = experience[:max_roles]

        # Limit bullets per role
        max_bullets = 3 if pages == 1 else 5

        optimized = []
        for exp in limited_exp:
            opt_exp = {**exp}

            # Limit description/achievements
            if 'achievements' in exp:
                opt_exp['achievements'] = exp['achievements'][:max_bullets]
            elif 'description' in exp:
                # Limit description words
                words = exp['description'].split()
                if len(words) > 50:
                    opt_exp['description'] = ' '.join(words[:50]) + '...'

            optimized.append(opt_exp)

        return optimized

    def _optimize_projects(
        self,
        projects: List[Dict],
        word_limit: int,
        pages: int
    ) -> List[Dict]:
        """Optimize projects section.

        Args:
            projects: List of project entries
            word_limit: Maximum words
            pages: Number of pages

        Returns:
            Optimized projects list
        """
        if not projects:
            return []

        # Limit number of projects
        max_projects = 2 if pages == 1 else 4

        optimized = []
        for project in projects[:max_projects]:
            opt_proj = {
                'title': project.get('title', ''),
                'technologies': project.get('technologies', [])[:5],  # Max 5 techs
                'highlights': project.get('highlights', [])[:2 if pages == 1 else 3],  # Limit highlights
                'description': project.get('description', '')[:100] if pages == 1 else project.get('description', '')[:200]
            }

            optimized.append(opt_proj)

        return optimized

    def _optimize_education(
        self,
        education: List[Dict],
        word_limit: int,
        pages: int
    ) -> List[Dict]:
        """Optimize education section.

        Args:
            education: List of education entries
            word_limit: Maximum words
            pages: Number of pages

        Returns:
            Optimized education list
        """
        if not education:
            return []

        # Limit number of degrees
        max_degrees = 2 if pages == 1 else 3

        optimized = []
        for edu in education[:max_degrees]:
            opt_edu = {
                'degree': edu.get('degree', ''),
                'institution': edu.get('institution', ''),
                'year': edu.get('year', ''),
                'field': edu.get('field', '')
            }

            # For 1-page CV, skip coursework
            if pages == 2 and 'coursework' in edu:
                opt_edu['coursework'] = edu['coursework'][:3]

            optimized.append(opt_edu)

        return optimized

    def _optimize_languages(self, languages: List[str], word_limit: int) -> List[str]:
        """Optimize languages section.

        Args:
            languages: List of languages
            word_limit: Maximum words

        Returns:
            Optimized languages list
        """
        if not languages:
            return []

        # Languages are usually compact, just limit to top 4
        return languages[:4]

    def _count_total_words(self, content: Dict) -> int:
        """Count total words in optimized content.

        Args:
            content: Content dictionary

        Returns:
            Total word count
        """
        total = 0

        # Count contact (estimated)
        if content.get('contact'):
            total += 20

        # Count summary
        if content.get('summary'):
            total += len(content['summary'].split())

        # Count skills (roughly 2 words per skill)
        if content.get('skills'):
            total += len(content['skills']) * 2

        # Count experience
        for exp in content.get('experience', []):
            total += len(exp.get('title', '').split())
            total += len(exp.get('company', '').split())
            if 'description' in exp:
                total += len(exp['description'].split())
            for ach in exp.get('achievements', []):
                total += len(ach.split())

        # Count projects
        for proj in content.get('projects', []):
            total += len(proj.get('title', '').split())
            total += len(proj.get('description', '').split())
            total += len(proj.get('technologies', [])) * 2
            for highlight in proj.get('highlights', []):
                total += len(highlight.split())

        # Count education
        for edu in content.get('education', []):
            total += 15  # Estimated per degree

        # Count languages
        total += len(content.get('languages', [])) * 2

        return total

    def _aggressive_optimize(
        self,
        content: Dict,
        limits: Dict,
        pages: int
    ) -> Dict:
        """Apply aggressive optimization to fit page limit.

        Args:
            content: Content dictionary
            limits: Word limits
            pages: Number of pages

        Returns:
            Aggressively optimized content
        """
        # Further reduce experience
        if len(content.get('experience', [])) > 2:
            content['experience'] = content['experience'][:2]

        # Further reduce projects
        if pages == 1 and len(content.get('projects', [])) > 1:
            content['projects'] = content['projects'][:1]

        # Shorten summary
        if content.get('summary'):
            words = content['summary'].split()
            content['summary'] = ' '.join(words[:30])

        # Reduce skills
        if len(content.get('skills', [])) > 8:
            content['skills'] = content['skills'][:8]

        return content


# Global instance
page_optimizer = PageOptimizer()
