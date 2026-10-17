"""Web 组合入口为可恢复任务装配领域处理器。"""
from .job_recovery import resume
from .web_library_processing import w_library_processing
from .web_scraping import w_scraping_cover
from .web_timeline_thumbnails import w_thumbnail_jobs
from .web_follow import w_follow_check
from .web_feeds import w_feed_check
from .web_wants import start_scrape
from apscheduler.schedulers.background import BackgroundScheduler


def restore(contract):
    return resume(contract.db_path, {
        "library-processing": lambda body: w_library_processing(contract, body, resume=True),
        "timeline-thumbnails": lambda body: w_thumbnail_jobs(contract, body),
        "scraping-cover": lambda body: w_scraping_cover(contract, body),
        "follow-check": lambda body: w_follow_check(contract, body),
        "feed-check": lambda body: w_feed_check(contract, body),
        "want-scrape": lambda _body: start_scrape(contract),
    })


class RecoveryService:
    """安装取消或完成后，现有服务也会接回等待中的任务。"""

    def __init__(self, contract, *, available):
        self.contract = contract
        self.available = available
        self.scheduler = BackgroundScheduler()

    def start(self):
        if self.available and not self.scheduler.running:
            self.scheduler.add_job(self.tick, 'interval', seconds=1,
                                   max_instances=1, coalesce=True)
            self.scheduler.start()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)

    def tick(self):
        from .update_tasks import is_pausing
        if not is_pausing(self.contract.db_path):
            restore(self.contract)
            self.contract.followups.resume_after_update()
