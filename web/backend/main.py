# ----- REQUIRED IMPORTS -----

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, SecretStr
from typing import Optional
import secrets
import os

from core.scraper_service import scrape_task
from core.helper import get_redis_connection, validate_credentials

# ----- SECURITY CONFIG -----

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
ENV = os.getenv("ENV", "development")

# ----- APPLICATION SETUP -----

app = FastAPI(
    title="Sagasu 2 API",
    description="FBS SMU Room Availability System",
    version="2.0",
    docs_url="/docs" if ENV == "development" else None,
    redoc_url=None
)

# ----- MODELS -----

class ScrapeRequest(BaseModel):
    buildings: list[str] = ["Li Ka Shing Library"]
    floors: list[str] = ["Level 1"]
    facility_types: list[str] = ["Classroom"]
    equipment: list[str] = ["Projector"]
    email: str
    password: SecretStr

class ScrapeResponse(BaseModel):
    task_id: str
    status_url: str

# ----- MIDDLEWARE -----

if ENV == "production":
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
    app.add_middleware(HTTPSRedirectMiddleware)

# ----- ENDPOINTS -----

@app.post("/scrape", response_model=ScrapeResponse)
async def trigger_scrape(
    request: ScrapeRequest, 
    api_key: Optional[str] = Depends(api_key_header)
):
    """Secure endpoint to initiate scraping"""
    if ENV == "production" and not validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    if not validate_credentials(request.email, request.password.get_secret()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials format"
        )
    try:
        task = scrape_task.delay({
            **request.dict(exclude={"password"}),
            "password": request.password.get_secret()
        })
        return {
            "task_id": task.id,
            "status_url": f"/tasks/{task.id}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Scraping service unavailable: {str(e)}"
        )

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Check status of a scraping task"""
    try:
        task = scrape_task.AsyncResult(task_id)
        response = {
            "task_id": task_id,
            "status": task.state,
            "ready": task.ready(),
            "successful": task.successful(),
        }

        if task.ready():
            response["result"] = task.result
            if task.failed():
                response["error"] = str(task.result)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found: {str(e)}"
        )

# ----- SECURITY HELPERS -----

def validate_api_key(api_key: Optional[str]) -> bool:
    """Validate API key against Redis store"""
    if ENV != "production":
        return True  
    redis = get_redis_connection()
    valid_key = redis.get(f"api_key:{api_key}")
    return valid_key is not None

# ----- HEALTH CHECK -----

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0"}

# ----- ENVIRONMENT INIT -----

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        ssl_keyfile=os.getenv("SSL_KEY_PATH"),
        ssl_certfile=os.getenv("SSL_CERT_PATH")
    )