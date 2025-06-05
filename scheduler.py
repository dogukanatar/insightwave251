# scheduler.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.email import EmailService
from services.database import get_subscribed_users, get_recent_papers

logger = logging.getLogger('INSTWAVE')


class SchedulerManager:
    def __init__(self, app):
        self.scheduler = BackgroundScheduler(timezone="Asia/Seoul")
        self.app = app
        self._configure_jobs()

    def _configure_jobs(self):
        """Configure scheduled jobs (작업 설정)"""
        # Weekly email job every Tuesday at 8am KST
        self.scheduler.add_job(
            id='weekly_email',
            func=self._send_weekly_emails,
            trigger=CronTrigger(
                day_of_week='tue',
                hour=8,
                minute=0,
                timezone="Asia/Seoul"
            ),
            max_instances=1
        )

        '''
        # Temporary test job (remove in production)
        self.scheduler.add_job(
            id='test_email',
            func=self._send_weekly_emails,
            trigger=CronTrigger(minute="*/5"),  # Every 5 minutes
            max_instances=1
        )
        '''
        logger.info("Scheduled jobs configured")

    def _send_weekly_emails(self):
        """Execute weekly email sending (주간 이메일 전송 실행)"""
        with self.app.app_context():
            try:
                logger.info("Starting weekly email dispatch...")
                users = get_subscribed_users()
                papers = get_recent_papers()

                if not papers:
                    logger.warning("No papers available for sending")
                    return

                for user in users:
                    email_content = self._generate_email_content(papers, user)
                    success = EmailService.send_research_digest(
                        email=user['email'],
                        content=email_content
                    )

                    if success:
                        logger.info(f"Email sent to {user['email']}")
                    else:
                        logger.error(f"Failed to send email to {user['email']}")

                logger.info(f"Successfully sent {len(users)} weekly emails")
            except Exception as e:
                logger.error(f"Weekly email failed: {str(e)}")

    def _generate_email_content(self, papers, user):
        """Generate personalized email content (개인화된 이메일 내용 생성)"""
        # user_papers = [p for p in papers]
        user_topic_ids = set(user['topics'])
        user_papers = [
            p for p in papers
            if set(p['topics']) & user_topic_ids
        ]

        if not user_papers:
            return f"""
            <div class="no-papers">
                <h3>Hello {user['name']},</h3>
                <p>There are no new papers in your topics this week.</p>
                <p>Check back next Tuesday for new research updates!</p>
            </div>
            """

        paper_items = "\n".join([
            f"""<div class="paper">
                <h3 class="paper-title">{p['title']}</h3>
                <p><strong>Authors:</strong> {p['authors']}</p>
                <p><strong>Published:</strong> {p['date']}</p>
                <p><strong>Summary:</strong> {p['summary'][:200]}...</p>
                <p><a href="{p['link']}">View Full Paper</a></p>
            </div>"""
            for p in user_papers
        ])

        return f"""
        <h2>Hello {user['name']},</h2>
        <p>Here are new papers in your topics this week:</p>
        <div class="papers-container">
            {paper_items}
        </div>
        """

    def start(self):
        """Start the scheduler (스케줄러 시작)"""
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler (스케줄러 종료)"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
