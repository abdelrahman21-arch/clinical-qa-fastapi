import logging

from fastapi import FastAPI

from .api import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = FastAPI(title="Clinical QA API")
app.include_router(api_router)
from .queue import redis_conn, logger  # import after logging configured


@app.on_event("startup")
def check_redis():
    try:
        redis_conn.ping()
        logger.info("redis connected host=%s port=%s db=%s", "localhost", 6379, 0)
    except Exception as exc:
        logger.warning("redis connection failed error=%s", exc)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
