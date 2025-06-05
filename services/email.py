# services/email.py
import resend
from flask import current_app
from pathlib import Path
from jinja2 import Template


class EmailService:
    @staticmethod
    def send_research_digest(email: str, content: str):
        """Send digest email using Resend API"""
        try:
            template_path = Path("templates/email_base.html")
            base_template = Template(template_path.read_text())

            final_html = base_template.render(
                content=content,
                unsubscribe_link="#"
            )

            resend.api_key = current_app.config['RESEND_API_KEY']

            response = resend.Emails.send({
                "from": "Research Digest <onboarding@resend.dev>",
                "to": email,
                "subject": "Your Weekly Research Briefing",
                "html": final_html
            })

            if 'id' in response:
                current_app.logger.info(f"Email sent to {email} successfully")
                return True
            else:
                current_app.logger.error(f"Email failed: {response.get('message', 'Unknown error')}")
                return False

        except Exception as e:
            current_app.logger.error(f"Email error: {str(e)}")
            return False
