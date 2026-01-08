import logging

from fastapi import FastAPI

from .api import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = FastAPI(title="Clinical QA API")
app.include_router(api_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
