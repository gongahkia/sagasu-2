from scraper import scrape_smu_fbs
from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery = Celery(__name__, broker=redis_url, backend=redis_url)

@celery.task(name="core.scrape_task")
def scrape_task(filters):
    """Shared scraping task with error handling"""
    try:
        result = scrape_smu_fbs(
            building_array=filters.get('buildings', []),
            floor_array=filters.get('floors', []),
            facility_type_array=filters.get('facility_types', []),
            equipment_array=filters.get('equipment', [])
        )
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}