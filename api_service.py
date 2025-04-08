from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import logging
import sys

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import route_to_segments module
try:
    from route_to_segments import plan_journey
    logger.info("Successfully imported route_to_segments module")
except Exception as e:
    logger.error(f"Error importing route_to_segments: {str(e)}")
    raise

app = FastAPI(title="Road Segment Booking API")

class JourneyRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    user_id: str
    journey_name: str
    start_time: datetime
    end_time: datetime

@app.post("/journey/plan")
async def create_journey(journey: JourneyRequest):
    """Plan and book a journey between two points"""
    logger.info(f"Received journey request from {journey.user_id}: {journey.journey_name}")
    
    try:
        result = plan_journey(
            journey.start_lat,
            journey.start_lon,
            journey.end_lat,
            journey.end_lon,
            journey.user_id,
            journey.journey_name,
            journey.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            journey.end_time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        if result['status'] == 'error':
            logger.error(f"Journey planning failed: {result['message']}")
            raise HTTPException(status_code=400, detail=result['message'])
        
        logger.info(f"Journey planned successfully with booking ID: {result['booking_id']}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing journey request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "ok", "message": "API is running"}

if __name__ == "__main__":
    logger.info("Starting Road Segment Booking API")
    uvicorn.run(app, host="0.0.0.0", port=8000)