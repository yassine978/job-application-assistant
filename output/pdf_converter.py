"""PDF conversion for CVs and cover letters."""

import markdown
from pathlib import Path
from typing import Optional
from datetime import datetime


class PDFConverter:
    """Convert markdown CVs to PDF with page control."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize PDF converter.

        Args:
            output_dir: Directory to save PDF files
        """
        if output_dir is None:
            from config import CVS_DIR
            output_dir = CVS_DIR

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def convert_markdown_to_pdf(
        self,
        markdown_content: str,
        output_filename: Optional[str] = None,
        max_pages: int = 1,
        title: Optional[str] = None
    ) -> Path:
        """Convert markdown content to PDF with page control.

        Args:
            markdown_content: Markdown formatted text
            output_filename: Output PDF filename (auto-generated if None)
            max_pages: Maximum number of pages allowed
            title: Document title

        Returns:
            Path to generated PDF file
        """
        try:
            from weasyprint import HTML, CSS
            from PyPDF2 import PdfReader

            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"cv_{timestamp}.pdf"

            output_path = self.output_dir / output_filename

            # Convert markdown to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=['extra', 'nl2br']
            )

            # Create HTML document with styling
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{title or 'CV'}</title>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # Define CSS for page control
            font_size = '10pt' if max_pages == 1 else '11pt'
            line_height = '1.3' if max_pages == 1 else '1.4'
            h1_size = '14pt' if max_pages == 1 else '16pt'
            h2_size = '12pt' if max_pages == 1 else '13pt'

            css = CSS(string=f'''
                @page {{
                    size: A4;
                    margin: 0.75in;
                }}
                body {{
                    font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;
                    font-size: {font_size};
                    line-height: {line_height};
                    color: #333;
                }}
                h1 {{
                    font-size: {h1_size};
                    margin-top: 0;
                    margin-bottom: 0.3em;
                    color: #2c3e50;
                }}
                h2 {{
                    font-size: {h2_size};
                    margin-top: 0.8em;
                    margin-bottom: 0.3em;
                    color: #34495e;
                    border-bottom: 1px solid #bdc3c7;
                    padding-bottom: 0.2em;
                }}
                h3 {{
                    font-size: 10pt;
                    margin-top: 0.5em;
                    margin-bottom: 0.2em;
                }}
                p {{
                    margin-top: 0.3em;
                    margin-bottom: 0.3em;
                }}
                ul {{
                    margin-top: 0.2em;
                    margin-bottom: 0.5em;
                    padding-left: 1.5em;
                }}
                li {{
                    margin-bottom: 0.2em;
                }}
                strong {{
                    font-weight: 600;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
            ''')

            # Generate PDF
            html = HTML(string=full_html)
            pdf_bytes = html.write_pdf(stylesheets=[css])

            # Write PDF to file
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)

            # Verify page count
            reader = PdfReader(output_path)
            actual_pages = len(reader.pages)

            if actual_pages > max_pages:
                print(f"Warning: PDF has {actual_pages} pages, limit was {max_pages}")
                # Note: In production, you might want to regenerate with stricter constraints

            return output_path

        except ImportError as e:
            # Fallback if weasyprint not installed
            print(f"Warning: PDF conversion requires weasyprint: {e}")
            print("Falling back to markdown file...")
            return self._save_as_markdown(markdown_content, output_filename)

        except Exception as e:
            print(f"Error converting to PDF: {e}")
            print("Falling back to markdown file...")
            return self._save_as_markdown(markdown_content, output_filename)

    def _save_as_markdown(
        self,
        markdown_content: str,
        output_filename: str
    ) -> Path:
        """Save content as markdown file (fallback).

        Args:
            markdown_content: Markdown text
            output_filename: Output filename

        Returns:
            Path to markdown file
        """
        # Change extension to .md
        md_filename = output_filename.replace('.pdf', '.md')
        output_path = self.output_dir / md_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return output_path

    def convert_cv_to_pdf(
        self,
        cv_content: str,
        job_title: str,
        company_name: str,
        cv_length: int = 1
    ) -> Path:
        """Convert CV to PDF with job-specific filename.

        Args:
            cv_content: CV markdown content
            job_title: Job title
            company_name: Company name
            cv_length: CV length in pages

        Returns:
            Path to generated PDF
        """
        # Sanitize filename
        safe_job = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_'))[:30]
        safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_'))[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"CV_{safe_company}_{safe_job}_{timestamp}.pdf"

        return self.convert_markdown_to_pdf(
            markdown_content=cv_content,
            output_filename=filename,
            max_pages=cv_length,
            title=f"CV - {job_title} at {company_name}"
        )

    def convert_cover_letter_to_pdf(
        self,
        letter_content: str,
        job_title: str,
        company_name: str
    ) -> Path:
        """Convert cover letter to PDF.

        Args:
            letter_content: Cover letter markdown content
            job_title: Job title
            company_name: Company name

        Returns:
            Path to generated PDF
        """
        # Sanitize filename
        safe_job = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_'))[:30]
        safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_'))[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"CoverLetter_{safe_company}_{safe_job}_{timestamp}.pdf"

        return self.convert_markdown_to_pdf(
            markdown_content=letter_content,
            output_filename=filename,
            max_pages=1,  # Cover letters are always 1 page
            title=f"Cover Letter - {job_title} at {company_name}"
        )

    def get_page_count(self, pdf_path: Path) -> int:
        """Get number of pages in PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of pages
        """
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return 0


# Global converter instance
pdf_converter = PDFConverter()
