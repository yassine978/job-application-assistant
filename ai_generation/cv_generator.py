"""CV generation with RAG and LLM support."""

from typing import Dict, Optional
from ai_generation.rag.rag_pipeline import rag_pipeline
from ai_generation.rag.page_optimizer import page_optimizer
from ai_generation.language_templates import language_templates
import os
from datetime import datetime


class CVGenerator:
    """Generate tailored CVs using RAG and LLM."""

    def __init__(self):
        """Initialize CV generator."""
        self.rag_pipeline = rag_pipeline
        self.page_optimizer = page_optimizer
        self.language_templates = language_templates
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
        language = cv_prefs.get('language', 'en')

        # Get language-specific section headers
        sections = self.language_templates.get_cv_sections(language)

        # Build CV markdown
        cv_parts = []

        # Header
        header_text = "CURRICULUM VITAE" if language == 'en' else "CURRICULUM VITAE"
        cv_parts.append(f"# {header_text}\n")

        # Contact (from profile context - simplified)
        cv_parts.append(f"## {sections['contact']}\n")
        cv_parts.append("[Contact details would be extracted from profile]\n")

        # Professional Summary
        cv_parts.append(f"## {sections['summary']}\n")
        if language == 'fr':
            cv_parts.append(
                f"Professionnel expérimenté recherchant un poste de {job_data.get('job_title')} "
                f"chez {job_data.get('company_name')}. "
                f"Solide expérience en {', '.join(job_data.get('required_skills', [])[:3])}.\n"
            )
        else:
            cv_parts.append(
                f"Experienced professional seeking a position as {job_data.get('job_title')} "
                f"at {job_data.get('company_name')}. "
                f"Strong background in {', '.join(job_data.get('required_skills', [])[:3])}.\n"
            )

        # Skills
        cv_parts.append(f"## {sections['skills']}\n")
        cv_parts.append("[Skills from profile context]\n")

        # Experience
        cv_parts.append(f"## {sections['experience']}\n")
        cv_parts.append("[Experience from profile context]\n")

        # Projects (if included)
        if context.get('selected_projects_data'):
            cv_parts.append(f"## {sections['projects']}\n")
            for proj_data in context['selected_projects_data']:
                proj = proj_data['project']
                cv_parts.append(f"### {proj['title']}\n")
                tech_label = "Technologies" if language == 'en' else "Technologies"
                cv_parts.append(f"**{tech_label}:** {', '.join(proj.get('technologies', [])[:5])}\n")
                cv_parts.append(f"{proj.get('description', '')[:200]}\n\n")

        # Education
        cv_parts.append(f"## {sections['education']}\n")
        cv_parts.append("[Education from profile context]\n")

        # Languages
        cv_parts.append(f"## {sections['languages']}\n")
        cv_parts.append("[Languages from profile context]\n")

        cv_content = '\n'.join(cv_parts)

        # Add note about page optimization
        target_pages = cv_prefs.get('cv_length', 1)
        opt_text = f"Optimized for {target_pages} page(s)" if language == 'en' else f"Optimisé pour {target_pages} page(s)"
        cv_content += f"\n---\n*{opt_text}*\n"

        return cv_content

    def _generate_with_llm(self, context: Dict) -> str:
        """Generate CV using Groq LLM.

        Args:
            context: Context dictionary from RAG pipeline

        Returns:
            CV content as markdown
        """
        cv_prefs = context['cv_preferences']
        language = cv_prefs.get('language', 'en')
        lang_name = "English" if language == 'en' else "French"

        print(f"  Using LLM-based generation (Groq) in {lang_name}")

        try:
            from groq import Groq

            client = Groq(api_key=self.groq_api_key)

            # Build prompt
            prompt = self._build_cv_prompt(context)

            # Language-specific system message
            system_msg = (
                "You are an expert CV writer. Generate professional, ATS-friendly CVs in markdown format."
                if language == 'en' else
                "Vous êtes un expert en rédaction de CV. Générez des CV professionnels et compatibles ATS au format markdown."
            )

            # Call LLM
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": system_msg
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

            print(f"  Generated {len(cv_content)} characters in {lang_name}")

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
        language = cv_prefs.get('language', 'en')

        # Get language-specific prompt template
        prompt_template = self.language_templates.get_cv_prompt(language)

        # Fill in the template
        prompt = prompt_template.format(
            job_title=job_data.get('job_title', ''),
            company_name=job_data.get('company_name', ''),
            job_description=job_data.get('description', '')[:500],
            required_skills=', '.join(job_data.get('required_skills', [])[:10]),
            profile=context.get('profile', ''),
            projects=context.get('projects', 'No projects selected'),
            cv_length=cv_prefs.get('cv_length', 1),
            include_projects=cv_prefs.get('include_projects', True)
        )

        return prompt


# Global instance
cv_generator = CVGenerator()
