import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.email import EmailService
from services.kakao import KakaoService
from services.database import get_subscribed_users, get_recent_papers
from services.ai_summary import generate_ai_summaries
from services.content_generator import generate_email_content

logger = logging.getLogger('INSTWAVE')

class SchedulerManager:
    def __init__(self, app):
        self.scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        self.app = app
        self._configure_jobs()

    def _configure_jobs(self):
        self.scheduler.add_job(
            id='weekly_ai_summary',
            func=self._generate_ai_summaries_job,
            trigger=CronTrigger(
                day_of_week='tue',
                hour=7,
                minute=0,
                timezone="Asia/Seoul"
            ),
            max_instances=1
        )
        self.scheduler.add_job(
            id='weekly_notification',
            func=self._send_weekly_notifications,
            trigger=CronTrigger(
                day_of_week='tue',
                hour=8,
                minute=0,
                timezone="Asia/Seoul"
            ),
            max_instances=1
        )
        logger.info("Scheduled jobs configured")

    def _send_weekly_notifications(self):
        with self.app.app_context():
            try:
                logger.info("Starting weekly notification dispatch...")
                users = get_subscribed_users()
                papers = get_recent_papers()
                for user in users:
                    if not user.get('active', True):
                        logger.info(f"Skipping inactive user: {user['email']}")
                        continue
                    email_content = self._generate_email_content(papers, user)
                    if user['notification_method'] in ['email', 'both']:
                        success = EmailService.send_research_digest(user, email_content)
                        if success:
                            logger.info(f"Email sent to {user['email']}")
                        else:
                            logger.error(f"Failed to send email to {user['email']}")
                    if user['notification_method'] in ['kakao', 'both']:
                        success = KakaoService.send_research_digest(user, email_content)
                        if success:
                            logger.info(f"Kakao notification sent to {user['email']}")
                        else:
                            logger.error(f"Failed to send Kakao to {user['email']}")
                logger.info(f"Successfully processed {len(users)} users")
            except Exception as e:
                logger.error(f"Weekly notification failed: {str(e)}")

    def _generate_ai_summaries_job(self):
        with self.app.app_context():
            try:
                logger.info("Starting AI summary generation...")
                generate_ai_summaries()
                logger.info("AI summary generation completed.")
            except Exception as e:
                logger.error(f"AI summary generation failed: {str(e)}")

    def start(self):
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
