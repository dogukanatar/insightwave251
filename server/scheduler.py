import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.database import get_subscribed_users, get_recent_papers
from services.core_services import ContentService, EmailService, KakaoService

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
            trigger=CronTrigger(day_of_week='tue', hour=7, minute=0),
            max_instances=1
        )
        self.scheduler.add_job(
            id='weekly_notification',
            func=self._send_weekly_notifications,
            trigger=CronTrigger(day_of_week='tue', hour=8, minute=0),
            max_instances=1
        )
        logger.info("Scheduled jobs configured")

    def _send_weekly_notifications(self):
        with self.app.app_context():
            try:
                logger.info("开始发送每周通知...")
                users = get_subscribed_users()
                papers = get_recent_papers()

                for target_user in users:
                    if not target_user.get('active', True):
                        logger.info(f"用户 {target_user['id']} 未激活，跳过")
                        continue

                    logger.info(f"处理用户 {target_user['id']} ({target_user['email']})")

                    email_content = ContentService.generate_email_content(papers, target_user)

                    if target_user['notification_method'] in ['email', 'both']:
                        logger.info(f"为用户 {target_user['id']} 发送邮件")
                        success = EmailService.send_research_digest(target_user, email_content)
                        logger.info(f"邮件发送结果: {'成功' if success else '失败'}")

                    if target_user['notification_method'] in ['kakao', 'both']:
                        logger.info(f"为用户 {target_user['id']} 发送Kakao消息")
                        success = KakaoService.send_research_digest(target_user, email_content)
                        logger.info(f"Kakao发送结果: {'成功' if success else '失败'}")

                logger.info(f"成功处理 {len(users)} 个用户")
            except Exception as e:
                logger.error(f"每周通知失败: {str(e)}")

    def _generate_ai_summaries_job(self):
        with self.app.app_context():
            try:
                logger.info("Starting AI summary generation...")
                self._generate_ai_summaries()
                logger.info("AI summary generation completed.")
            except Exception as e:
                logger.error(f"AI summary generation failed: {str(e)}")

    def _generate_ai_summaries(self):
        from services.core_services import AISummaryService
        AISummaryService.generate_ai_summaries()

    def start(self):
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
