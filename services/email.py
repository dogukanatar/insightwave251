import resend
from flask import current_app, url_for
from pathlib import Path
from jinja2 import Template
import logging
from i18n import get_translation

logger = logging.getLogger('INSTWAVE')


class EmailService:
    @staticmethod
    def send_research_digest(user, content):
        try:
            if user['language'] == 'ko':
                subject = get_translation('email_subject', 'ko')
            else:
                subject = get_translation('email_subject', 'en')

            template_path = Path("templates/email_base.html")
            base_template = Template(template_path.read_text())

            unsubscribe_link = url_for('dashboard', _external=True)

            final_html = base_template.render(
                content=content,
                unsubscribe_link=unsubscribe_link,
                user_name=user['name'],
                _=lambda key: get_translation(key, user['language'])
            )

            resend.api_key = current_app.config['RESEND_API_KEY']

            response = resend.Emails.send({
                "from": "INSTWAVE Digest <onboarding@resend.dev>",
                "to": user['email'],
                "subject": subject,
                "html": final_html
            })

            if 'id' in response:
                logger.info(f"Email sent to {user['email']} successfully")
                return True
            else:
                logger.error(f"Email failed: {response.get('message', 'Unknown error')}")
                return False

        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            return False
