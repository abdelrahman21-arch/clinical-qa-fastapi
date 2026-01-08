from redis import Redis
from rq import Queue

from .settings import settings

redis_conn = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
)
queue = Queue("qa", connection=redis_conn)
