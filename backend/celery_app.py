from celery import Celery
from celery.schedules import crontab
import os

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "studentlabs",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.generation_tasks", "tasks.export_tasks"]
)

# Celery Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    result_expires=3600,  # Results expire after 1 hour
)

# Beat Schedule (for periodic tasks, if needed later)
celery_app.conf.beat_schedule = {
    # Example: Check pending tasks every 5 minutes
    'check-pending-tasks': {
        'task': 'tasks.generation_tasks.check_pending_tasks',
        'schedule': crontab(minute='*/5'),
    },
}
