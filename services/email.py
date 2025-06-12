# services/email.py
import resend
from flask import current_app
from pathlib import Path
from jinja2 import Template
from .translation import translate_content
import logging

logger = logging.getLogger('INSTWAVE')


class EmailService:
    @staticmethod
    def send_research_digest(user, content):
        """Send digest email using Resend API"""
        try:
            if user['language'] == 'ko':
                content = translate_content(content, 'en', 'ko')

                subject = "INSTWAVE 연구 요약 리포트"
                content = content.replace('<h2>', '')
            else:
                subject = "INSTWAVE Research Digest"
                content = content.replace('<h2>Hello', '').replace('<h2>', '')

            template_path = Path("templates/email_base.html")
            base_template = Template(template_path.read_text())

            final_html = base_template.render(
                content=content,
                unsubscribe_link="#"
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



class KakaoService:
    @staticmethod
    def send_research_digest(user, content):
        """Placeholder for Kakao notification service"""
        try:
            # TODO: Implement Kakao API integration
            logger.info(f"[KAKAO] Would send to {user['email']}: {content[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Kakao error: {str(e)}")
            return False
