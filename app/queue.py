import logging

from redis import Redis
from rq import Queue

from .settings import settings

logger = logging.getLogger("app.queue")
redis_conn = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
)
try:
    redis_conn.ping()
    logger.info(
        "redis connected host=%s port=%s db=%s",
        settings.redis_host,
        settings.redis_port,
        settings.redis_db,
    )
except Exception as exc:
    logger.warning(
        "redis connection failed host=%s port=%s db=%s error=%s",
        settings.redis_host,
        settings.redis_port,
        settings.redis_db,
        exc,
    )
queue = Queue("qa", connection=redis_conn)
