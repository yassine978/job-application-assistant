"""Cover letter generation with RAG and LLM support."""

from typing import Dict
from ai_generation.rag.rag_pipeline import rag_pipeline
import os
from datetime import datetime


class CoverLetterGenerator:
    """Generate tailored cover letters using RAG and LLM."""

    def __init__(self):
        """Initialize cover letter generator."""
        self.rag_pipeline = rag_pipeline
        self.groq_api_key = os.getenv('GROQ_API_KEY')

    def initialize(self):
        """Initialize dependencies."""
        self.rag_pipeline.initialize()
        print("[OK] Cover Letter Generator initialized")

    def generate_cover_letter(
        self,
        user_id: str,
        job: Dict,
        use_llm: bool = False
    ) -> Dict:
        """Generate a tailored cover letter for a job.

        Args:
            user_id: User ID
            job: Job dictionary
            use_llm: Whether to use LLM for generation

        Returns:
            Dictionary with cover letter content and metadata
        """
        print(f"\n[COVER LETTER GENERATOR] Generating letter for: {job.get('job_title')}")

        # Build context using RAG
        context = self.rag_pipeline.build_context_for_cover_letter(
            user_id=user_id,
            job=job
        )

        if use_llm and self.groq_api_key:
            # Use LLM
            letter_content = self._generate_with_llm(context)
        else:
            # Use template
            letter_content = self._generate_with_template(context)

        # Metadata
        metadata = {
            'user_id': user_id,
            'job_id': job.get('id'),
            'job_title': job.get('job_title'),
            'company': job.get('company_name'),
            'projects_mentioned': len(context['selected_projects_data']),
            'generated_at': datetime.now().isoformat(),
            'method': 'llm' if (use_llm and self.groq_api_key) else 'template'
        }

        return {
            'content': letter_content,
            'metadata': metadata,
            'context': context
        }

    def _generate_with_template(self, context: Dict) -> str:
        """Generate cover letter using template.

        Args:
            context: Context dictionary from RAG pipeline

        Returns:
            Cover letter content
        """
        print("  Using template-based generation")

        job_data = context['job_data']

        letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_data.get('job_title')} position at {job_data.get('company_name')}.

[Profile context would be used here to create personalized introduction]

My experience aligns well with your requirements, particularly in {', '.join(job_data.get('required_skills', [])[:3])}.

"""

        # Mention relevant projects if any
        if context.get('selected_projects_data'):
            letter += "\nSome highlights of my relevant work:\n"
            for proj_data in context['selected_projects_data'][:2]:
                proj = proj_data['project']
                letter += f"\n- {proj['title']}: {proj.get('description', '')[:100]}\n"

        letter += f"""
I am excited about the opportunity to contribute to {job_data.get('company_name')} and would welcome the chance to discuss how my skills and experience can benefit your team.

Thank you for considering my application.

Best regards,
[Name from profile]
"""

        return letter

    def _generate_with_llm(self, context: Dict) -> str:
        """Generate cover letter using Groq LLM.

        Args:
            context: Context dictionary from RAG pipeline

        Returns:
            Cover letter content
        """
        print("  Using LLM-based generation (Groq)")

        try:
            from groq import Groq

            client = Groq(api_key=self.groq_api_key)

            # Build prompt
            prompt = self._build_cover_letter_prompt(context)

            # Call LLM
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cover letter writer. Write compelling, professional cover letters that highlight relevant experience."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # Slightly higher for more creative writing
                max_tokens=1000
            )

            letter_content = response.choices[0].message.content

            print(f"  Generated {len(letter_content)} characters")

            return letter_content

        except ImportError:
            print("  [WARNING] Groq library not installed, falling back to template")
            return self._generate_with_template(context)
        except Exception as e:
            print(f"  [ERROR] LLM generation failed: {e}, falling back to template")
            return self._generate_with_template(context)

    def _build_cover_letter_prompt(self, context: Dict) -> str:
        """Build prompt for LLM cover letter generation.

        Args:
            context: Context dictionary

        Returns:
            Prompt string
        """
        job_data = context['job_data']

        prompt = f"""Write a compelling cover letter for this job application.

=== JOB INFORMATION ===
Position: {job_data.get('job_title')}
Company: {job_data.get('company_name')}
Location: {job_data.get('location')}
Description: {job_data.get('description', '')[:400]}

=== CANDIDATE PROFILE ===
{context['profile']}

=== RELEVANT PROJECTS TO MENTION ===
{context.get('projects', 'No specific projects to highlight')}

=== INSTRUCTIONS ===
1. Write a professional, enthusiastic cover letter (300-400 words)
2. Address it to "Hiring Manager"
3. Express genuine interest in the role
4. Highlight 2-3 most relevant experiences/skills
5. Mention 1-2 relevant projects if provided
6. Show knowledge of the company (based on job description)
7. Explain why you're a great fit
8. Close with a call to action
9. Keep tone professional but personable
10. Use the candidate's actual experience from the profile

Write the cover letter now:"""

        return prompt


# Global instance
cover_letter_generator = CoverLetterGenerator()
