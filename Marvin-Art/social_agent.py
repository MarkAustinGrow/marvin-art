import os
from dotenv import load_dotenv
from supabase import create_client, Client, __version__ as supabase_version
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import schedule
from threading import Thread
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Marvin Social Agent",
    description="API for managing social media posts and feedback",
    version="1.0.0"
)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Debug connection information
print(f"Supabase URL: {supabase_url}")
print(f"Supabase Key: {supabase_key[:10]}... (truncated)")
print(f"Supabase Python library version: {supabase_version}")

try:
    # Initialize Supabase client with only the required parameters
    # Explicitly avoiding any proxy settings
    supabase = create_client(
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    print("Successfully initialized Supabase client")
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}")
    print("Please check your Supabase URL and API key.")
    import sys
    sys.exit(1)

# Constants
MAX_POSTS_PER_DAY = 2
POSTING_INTERVAL_HOURS = 12

class SocialAgent:
    def __init__(self):
        self.posted_images = set()
        self.load_posted_images()

    def load_posted_images(self):
        """Load IDs of images that have already been posted"""
        try:
            response = supabase.table('feedback').select('image_id').execute()
            self.posted_images = {item['image_id'] for item in response.data}
        except Exception as e:
            print(f"Error loading posted images: {str(e)}")

    def get_posted_images_today(self) -> int:
        """Get count of images posted today"""
        try:
            today = datetime.now().date()
            response = supabase.table('feedback').select('id').gte('created_at', today.isoformat()).execute()
            return len(response.data)
        except Exception as e:
            print(f"Error getting posted images count: {str(e)}")
            return 0

    def get_unposted_images(self) -> List[Dict[str, Any]]:
        """Get list of images that haven't been posted yet"""
        try:
            response = supabase.table('images').select('*').not_.in_('id', list(self.posted_images)).execute()
            return response.data
        except Exception as e:
            print(f"Error getting unposted images: {str(e)}")
            return []

    def post_image(self, image_data: Dict[str, Any]) -> bool:
        """Post an image to social media and record feedback"""
        try:
            # Here you would implement the actual social media posting
            # For now, we'll just record it in the feedback table
            feedback_data = {
                'image_id': image_data['id'],
                'posted_at': datetime.now().isoformat(),
                'platform': 'twitter',  # or whatever platform you're using
                'status': 'posted'
            }
            
            response = supabase.table('feedback').insert(feedback_data).execute()
            if response.data:
                self.posted_images.add(image_data['id'])
                return True
            return False
        except Exception as e:
            print(f"Error posting image: {str(e)}")
            return False

    def auto_post(self):
        """Automatically post images based on schedule"""
        try:
            # Check daily limit
            if self.get_posted_images_today() >= MAX_POSTS_PER_DAY:
                print("Daily post limit reached")
                return

            # Get unposted images
            unposted_images = self.get_unposted_images()
            if not unposted_images:
                print("No unposted images available")
                return

            # Select a random image to post
            import random
            image_to_post = random.choice(unposted_images)
            
            # Post the image
            if self.post_image(image_to_post):
                print(f"Successfully posted image {image_to_post['id']}")
            else:
                print(f"Failed to post image {image_to_post['id']}")
        except Exception as e:
            print(f"Error in auto_post: {str(e)}")

# Initialize social agent
social_agent = SocialAgent()

# Schedule auto-posting
schedule.every(POSTING_INTERVAL_HOURS).hours.do(social_agent.auto_post)

# Run scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# API endpoints
@app.post("/post")
async def create_post(image_id: str):
    """Manually trigger a post for a specific image"""
    try:
        # Check daily limit
        if social_agent.get_posted_images_today() >= MAX_POSTS_PER_DAY:
            raise HTTPException(status_code=429, detail="Daily post limit reached")

        # Get image data
        response = supabase.table('images').select('*').eq('id', image_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Image not found")

        # Post the image
        if social_agent.post_image(response.data[0]):
            return {"status": "success", "message": f"Image {image_id} posted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to post image")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get posting statistics"""
    try:
        posted_today = social_agent.get_posted_images_today()
        unposted_count = len(social_agent.get_unposted_images())
        return {
            "posted_today": posted_today,
            "unposted_count": unposted_count,
            "max_posts_per_day": MAX_POSTS_PER_DAY,
            "posting_interval_hours": POSTING_INTERVAL_HOURS
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
