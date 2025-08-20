"""
scheduler.py

Provides scheduling capabilities for Director-AI.
Supports both simple interval scheduling (APScheduler) and cron-based scheduling.
"""

from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import time
from typing import Callable, Optional

class DirectorAIScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def schedule_interval(self, func: Callable, interval_seconds: int):
        """Schedule a function to run at a fixed interval (in seconds)"""
        self.scheduler.add_job(func, 'interval', seconds=interval_seconds)

    def schedule_cron(self, func: Callable, cron_expr: str):
        """Schedule a function using a cron expression (e.g., '0 0 * * *')"""
        # APScheduler uses separate fields for cron, so parse the string
        fields = cron_expr.strip().split()
        if len(fields) != 5:
            raise ValueError("Cron expression must have 5 fields (min hour day month weekday)")
        minute, hour, day, month, weekday = fields
        self.scheduler.add_job(func, 'cron', minute=minute, hour=hour, day=day, month=month, day_of_week=weekday)

    def stop(self):
        self.scheduler.shutdown()

# Example usage:
# def my_task():
#     print("Task executed at", time.ctime())
#
# scheduler = DirectorAIScheduler()
# scheduler.schedule_interval(my_task, interval_seconds=3600)  # Every hour
# scheduler.schedule_cron(my_task, '0 0 * * *')  # Every day at midnight
