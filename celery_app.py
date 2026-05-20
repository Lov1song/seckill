from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    "tasks",
    broker=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0",
    backend=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/1",
    include=["tasks.order_tasks", "tasks.alert_tasks"] 
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="Asia/Shanghai"
)

celery.conf.beat_schedule = {
    "update-activity-status": {
        "task": "tasks.order_tasks.update_activity_status",
        "schedule": 60.0
    },
    "check-price-alerts": {
        "task": "tasks.alert_tasks.check_price_alerts",
        "schedule": 3600.0  # 每小时检查一次
    }
}
