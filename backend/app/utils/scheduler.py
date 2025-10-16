from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.scraper_service import scraper_service
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_scrape():
    """
    Scheduled task to scrape opportunities daily
    """
    logger.info("Starting scheduled opportunity scraping...")
    
    db = SessionLocal()
    try:
        results = await scraper_service.scrape_all_sources(db)
        logger.info(f"Scraping completed: {results}")
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
    finally:
        db.close()

def start_scheduler():
    """
    Start the scheduler
    Runs scraping daily at 2 AM
    """
    # Schedule scraping every day at 2 AM
    scheduler.add_job(
        scheduled_scrape,
        CronTrigger(hour=2, minute=0),
        id="daily_scrape",
        name="Daily opportunity scraping",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - Daily scraping at 2 AM")

def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
