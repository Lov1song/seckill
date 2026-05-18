from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    "tasks",
    broker=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0",
    backend=f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/1",
    include=["tasks.order_tasks"]
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="Asia/Shanghai"
)