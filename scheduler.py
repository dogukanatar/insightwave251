# scheduler.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.email import EmailService
from services.mock_data import get_subscribed_users, get_recent_papers

logger = logging.getLogger('INSTWAVE')

class SchedulerManager:
    def __init__(self, app):
        self.scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        self.app = app
        self._configure_jobs()

    def _configure_jobs(self):
        """Configure scheduled jobs"""
        # Email job at 8am KST
        self.scheduler.add_job(
            id='daily_email',
            func=self._send_daily_emails,
            trigger=CronTrigger(hour=8, minute=0, timezone="Asia/Seoul"),
            # trigger=CronTrigger(minute="*/1", timezone="Asia/Seoul"), # every min
            max_instances=1
        )
        # Crawling job at 12am KST (placeholder)
        self.scheduler.add_job(
            id='daily_crawl',
            func=self._mock_crawling_task,
            trigger=CronTrigger(hour=0, timezone="Asia/Seoul")
        )
        logger.info("Scheduled jobs configured")

    def _send_daily_emails(self):
        """Execute email sending task"""
        with self.app.app_context():
            try:
                logger.info("Starting scheduled email dispatch...")
                users = get_subscribed_users()
                papers = get_recent_papers()

                if not papers:
                    logger.warning("No papers available for sending")
                    return

                for user in users:
                    email_content = self._generate_email_content(papers)
                    EmailService.send_research_digest(
                        email=user['email'],
                        content=email_content
                    )
                    logger.info(f"Email sent to {user['email']}")

                logger.info(f"Successfully sent {len(users)} emails")
            except Exception as e:
                logger.error(f"Scheduled email failed: {str(e)}")

    def _mock_crawling_task(self):
        """Placeholder for crawling task"""
        logger.info("Crawling task triggered (mock implementation)")
        # TODO: Replace with real crawling logic

    def _generate_email_content(self, papers):
        """Generate email HTML content"""
        paper_items = "\n".join([
            f"""<div class="paper">
                <h3>{p['title']}</h3>
                <p>Authors: {', '.join(p['authors'])}</p>
                <p>Published: {p['date']}</p>
                <a href="{p['link']}">View Paper</a>
            </div>"""
            for p in papers
        ])
        return f"<h2>Latest Research Papers</h2>{paper_items}"

    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
