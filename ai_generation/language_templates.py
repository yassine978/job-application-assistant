"""Language templates for CV and cover letter generation."""

from typing import Dict


class LanguageTemplates:
    """Templates for multi-language CV and cover letter generation."""

    def __init__(self):
        """Initialize language templates."""
        self.templates = {
            'en': self._get_english_templates(),
            'fr': self._get_french_templates()
        }

    def get_cv_sections(self, language: str = 'en') -> Dict[str, str]:
        """Get CV section headers for specified language.

        Args:
            language: Language code ('en' or 'fr')

        Returns:
            Dictionary with section headers
        """
        return self.templates.get(language, self.templates['en'])['cv_sections']

    def get_cv_prompt(self, language: str = 'en') -> str:
        """Get CV generation prompt for LLM.

        Args:
            language: Language code ('en' or 'fr')

        Returns:
            Prompt template string
        """
        return self.templates.get(language, self.templates['en'])['cv_prompt']

    def get_cover_letter_prompt(self, language: str = 'en') -> str:
        """Get cover letter generation prompt for LLM.

        Args:
            language: Language code ('en' or 'fr')

        Returns:
            Prompt template string
        """
        return self.templates.get(language, self.templates['en'])['cover_letter_prompt']

    def _get_english_templates(self) -> Dict:
        """Get English language templates.

        Returns:
            Dictionary with English templates
        """
        return {
            'cv_sections': {
                'profile': 'Professional Profile',
                'experience': 'Professional Experience',
                'education': 'Education',
                'skills': 'Technical Skills',
                'projects': 'Key Projects',
                'languages': 'Languages',
                'contact': 'Contact',
                'summary': 'Professional Summary'
            },
            'cv_prompt': """Generate a professional CV/resume in English tailored for the job posting.

=== JOB INFORMATION ===
Position: {job_title}
Company: {company_name}
Description: {job_description}
Required Skills: {required_skills}

=== CANDIDATE PROFILE ===
{profile}

=== SELECTED PROJECTS ===
{projects}

=== CV PREFERENCES ===
- CV Length: {cv_length} page(s)
- Include Projects: {include_projects}

=== INSTRUCTIONS ===
1. Generate a professional CV in English
2. Keep it to {cv_length} page(s) maximum
3. Focus on experience and skills relevant to the job
4. Highlight achievements with metrics where possible
5. Use professional, concise language
6. Format in clean markdown
7. Include these sections in order:
   - Professional Summary (2-3 sentences)
   - Professional Experience (most relevant roles)
   - Education
   - Technical Skills (prioritize job-relevant skills)
   - Key Projects (only if include_projects is True)
   - Languages
8. Tailor content to match job requirements
9. Use bullet points for responsibilities and achievements
10. Be specific and quantify achievements when possible

Generate the CV now in markdown format:""",
            'cover_letter_prompt': """Write a professional cover letter in English for this job application.

=== JOB INFORMATION ===
Position: {job_title}
Company: {company_name}
Location: {location}
Description: {description}

=== CANDIDATE PROFILE ===
{profile}

=== RELEVANT PROJECTS ===
{projects}

=== INSTRUCTIONS ===
1. Write a professional, enthusiastic cover letter in English (300-400 words)
2. Address it to "Hiring Manager" or "Hiring Team"
3. Express genuine interest in the role
4. Highlight 2-3 most relevant experiences/skills
5. Mention 1-2 relevant projects if provided
6. Show knowledge of the company (based on job description)
7. Explain why you're a great fit
8. Close with a call to action
9. Keep tone professional but personable
10. Use the candidate's actual experience from the profile

Write the cover letter now:"""
        }

    def _get_french_templates(self) -> Dict:
        """Get French language templates.

        Returns:
            Dictionary with French templates
        """
        return {
            'cv_sections': {
                'profile': 'Profil Professionnel',
                'experience': 'Expérience Professionnelle',
                'education': 'Formation',
                'skills': 'Compétences Techniques',
                'projects': 'Projets Clés',
                'languages': 'Langues',
                'contact': 'Contact',
                'summary': 'Résumé Professionnel'
            },
            'cv_prompt': """Générez un CV professionnel en français adapté à l'offre d'emploi.

=== INFORMATIONS SUR LE POSTE ===
Poste: {job_title}
Entreprise: {company_name}
Description: {job_description}
Compétences Requises: {required_skills}

=== PROFIL DU CANDIDAT ===
{profile}

=== PROJETS SÉLECTIONNÉS ===
{projects}

=== PRÉFÉRENCES CV ===
- Longueur du CV: {cv_length} page(s)
- Inclure les Projets: {include_projects}

=== INSTRUCTIONS ===
1. Générez un CV professionnel en français
2. Limitez-le à {cv_length} page(s) maximum
3. Concentrez-vous sur l'expérience et les compétences pertinentes pour le poste
4. Mettez en évidence les réalisations avec des métriques si possible
5. Utilisez un langage professionnel et concis
6. Formatez en markdown propre
7. Incluez ces sections dans l'ordre:
   - Résumé Professionnel (2-3 phrases)
   - Expérience Professionnelle (postes les plus pertinents)
   - Formation
   - Compétences Techniques (priorisez les compétences liées au poste)
   - Projets Clés (seulement si include_projects est True)
   - Langues
8. Adaptez le contenu aux exigences du poste
9. Utilisez des puces pour les responsabilités et réalisations
10. Soyez spécifique et quantifiez les réalisations lorsque possible

Générez le CV maintenant au format markdown:""",
            'cover_letter_prompt': """Rédigez une lettre de motivation professionnelle en français pour cette candidature.

=== INFORMATIONS SUR LE POSTE ===
Poste: {job_title}
Entreprise: {company_name}
Localisation: {location}
Description: {description}

=== PROFIL DU CANDIDAT ===
{profile}

=== PROJETS PERTINENTS ===
{projects}

=== INSTRUCTIONS ===
1. Rédigez une lettre de motivation professionnelle et enthousiaste en français (300-400 mots)
2. Adressez-la à "Madame, Monsieur" ou "L'équipe de recrutement"
3. Exprimez un intérêt sincère pour le poste
4. Mettez en avant 2-3 expériences/compétences les plus pertinentes
5. Mentionnez 1-2 projets pertinents si fournis
6. Montrez votre connaissance de l'entreprise (basée sur la description du poste)
7. Expliquez pourquoi vous êtes un excellent candidat
8. Concluez avec un appel à l'action
9. Gardez un ton professionnel mais personnel
10. Utilisez l'expérience réelle du candidat tirée du profil

Rédigez la lettre de motivation maintenant:"""
        }


# Global instance
language_templates = LanguageTemplates()
