"""CV generation with RAG and LLM support."""

from typing import Dict, Optional
from ai_generation.rag.rag_pipeline import rag_pipeline
from ai_generation.rag.page_optimizer import page_optimizer
import os
from datetime import datetime


class CVGenerator:
    """Generate tailored CVs using RAG and LLM."""

    def __init__(self):
        """Initialize CV generator."""
        self.rag_pipeline = rag_pipeline
        self.page_optimizer = page_optimizer
        self.groq_api_key = os.getenv('GROQ_API_KEY')

    def initialize(self):
        """Initialize dependencies."""
        self.rag_pipeline.initialize()
        print("[OK] CV Generator initialized")

    def generate_cv(
        self,
        user_id: str,
        job: Dict,
        cv_preferences: Optional[Dict] = None,
        use_llm: bool = False
    ) -> Dict:
        """Generate a tailored CV for a job.

        Args:
            user_id: User ID
            job: Job dictionary
            cv_preferences: CV preferences
            use_llm: Whether to use LLM for generation (requires GROQ_API_KEY)

        Returns:
            Dictionary with CV content and metadata
        """
        print(f"\n[CV GENERATOR] Generating CV for: {job.get('job_title')}")

        # Build context using RAG
        context = self.rag_pipeline.build_context_for_cv(
            user_id=user_id,
            job=job,
            cv_preferences=cv_preferences
        )

        if use_llm and self.groq_api_key:
            # Use LLM to generate CV
            cv_content = self._generate_with_llm(context)
        else:
            # Use template-based generation
            cv_content = self._generate_with_template(context)

        # Metadata
        metadata = {
            'user_id': user_id,
            'job_id': job.get('id'),
            'job_title': job.get('job_title'),
            'company': job.get('company_name'),
            'cv_length': context['cv_preferences'].get('cv_length', 1),
            'projects_included': len(context['selected_projects_data']),
            'projects_metadata': [
                {
                    'project_id': p['project']['id'],
                    'title': p['project']['title'],
                    'relevance_score': p['relevance_score']
                }
                for p in context['selected_projects_data']
            ],
            'generated_at': datetime.now().isoformat(),
            'method': 'llm' if (use_llm and self.groq_api_key) else 'template'
        }

        return {
            'content': cv_content,
            'metadata': metadata,
            'context': context
        }

    def _generate_with_template(self, context: Dict) -> str:
        """Generate CV using template (fallback when no LLM).

        Args:
            context: Context dictionary from RAG pipeline

        Returns:
            CV content as markdown
        """
        print("  Using template-based generation (no LLM)")

        cv_prefs = context['cv_preferences']
        job_data = context['job_data']

        # Build CV markdown
        cv_parts = []

        # Header
        cv_parts.append("# CURRICULUM VITAE\n")

        # Contact (from profile context - simplified)
        cv_parts.append("## Contact Information\n")
        cv_parts.append("[Contact details would be extracted from profile]\n")

        # Professional Summary
        cv_parts.append("## Professional Summary\n")
        cv_parts.append(
            f"Experienced professional seeking a position as {job_data.get('job_title')} "
            f"at {job_data.get('company_name')}. "
            f"Strong background in {', '.join(job_data.get('required_skills', [])[:3])}.\n"
        )

        # Skills
        cv_parts.append("## Technical Skills\n")
        cv_parts.append("[Skills from profile context]\n")

        # Experience
        cv_parts.append("## Professional Experience\n")
        cv_parts.append("[Experience from profile context]\n")

        # Projects (if included)
        if context.get('selected_projects_data'):
            cv_parts.append("## Projects\n")
            for proj_data in context['selected_projects_data']:
                proj = proj_data['project']
                cv_parts.append(f"### {proj['title']}\n")
                cv_parts.append(f"**Technologies:** {', '.join(proj.get('technologies', [])[:5])}\n")
                cv_parts.append(f"{proj.get('description', '')[:200]}\n\n")

        # Education
        cv_parts.append("## Education\n")
        cv_parts.append("[Education from profile context]\n")

        # Languages
        cv_parts.append("## Languages\n")
        cv_parts.append("[Languages from profile context]\n")

        cv_content = '\n'.join(cv_parts)

        # Add note about page optimization
        target_pages = cv_prefs.get('cv_length', 1)
        cv_content += f"\n---\n*Optimized for {target_pages} page(s)*\n"

        return cv_content

    def _generate_with_llm(self, context: Dict) -> str:
        """Generate CV using Groq LLM.

        Args:
            context: Context dictionary from RAG pipeline

        Returns:
            CV content as markdown
        """
        print("  Using LLM-based generation (Groq)")

        try:
            from groq import Groq

            client = Groq(api_key=self.groq_api_key)

            # Build prompt
            prompt = self._build_cv_prompt(context)

            # Call LLM
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert CV writer. Generate professional, ATS-friendly CVs in markdown format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            cv_content = response.choices[0].message.content

            print(f"  Generated {len(cv_content)} characters")

            return cv_content

        except ImportError:
            print("  [WARNING] Groq library not installed, falling back to template")
            return self._generate_with_template(context)
        except Exception as e:
            print(f"  [ERROR] LLM generation failed: {e}, falling back to template")
            return self._generate_with_template(context)

    def _build_cv_prompt(self, context: Dict) -> str:
        """Build prompt for LLM CV generation.

        Args:
            context: Context dictionary

        Returns:
            Prompt string
        """
        cv_prefs = context['cv_preferences']
        job_data = context['job_data']

        prompt = f"""Generate a professional CV tailored for this job application.

=== JOB INFORMATION ===
Position: {job_data.get('job_title')}
Company: {job_data.get('company_name')}
Location: {job_data.get('location')}
Type: {job_data.get('job_type')}
Required Skills: {', '.join(job_data.get('required_skills', [])[:10])}

Description: {job_data.get('description', '')[:500]}

=== USER PROFILE ===
{context['profile']}

=== SELECTED PROJECTS ===
{context.get('projects', 'No projects selected')}

=== CV REQUIREMENTS ===
- Length: {cv_prefs.get('cv_length', 1)} page(s) MAXIMUM
- Include Projects: {cv_prefs.get('include_projects', False)}
- Detail Level: {cv_prefs.get('project_detail_level', 'concise')}

=== INSTRUCTIONS ===
1. Create a professional CV in clean markdown format
2. Tailor content specifically to the job requirements
3. Highlight relevant skills and experience
4. CRITICAL: Must fit in {cv_prefs.get('cv_length', 1)} page(s)
5. Use the selected projects (already filtered for relevance)
6. Structure: Contact, Summary, Skills, Experience, Projects, Education, Languages
7. Be concise and impactful
8. Focus on achievements and metrics where possible

Generate the CV now:"""

        return prompt


# Global instance
cv_generator = CVGenerator()
