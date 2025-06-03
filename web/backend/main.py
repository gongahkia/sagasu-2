# ----- REQUIRED IMPORTS -----

from fastapi import FastAPI
from core.scraper_service import scrape_task
from pydantic import BaseModel

# ----- CLASS DEFINITIONS -----

app = FastAPI()

class ScrapeRequest(BaseModel):
    buildings: list[str]
    floors: list[str]
    facility_types: list[str]
    equipment: list[str]

@app.post("/scrape")
async def trigger_scrape(request: ScrapeRequest):
    task = scrape_task.delay(request.dict())
    return {"task_id": task.id}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = scrape_task.AsyncResult(task_id)
    return {
        "ready": task.ready(),
        "successful": task.successful(),
        "result": task.result if task.ready() else None
    }