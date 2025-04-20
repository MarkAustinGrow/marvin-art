from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import schedule
import time
import threading
from supabase import create_client, Client
import openai
import requests
from datetime import datetime, timedelta
import random

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Marvin Social Agent")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print(f"Successfully connected to Supabase at {supabase_url}")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    print("Please check your Supabase URL and API key.")
    supabase = None

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
MAX_POSTS_PER_DAY = 2
POSTING_INTERVAL_HOURS = 12

def get_posted_images_today():
    """Get count of images posted today"""
    if not supabase:
        return 0
    today = datetime.now().date()
    try:
        response = supabase.table('feedback').select('id').execute()
        return len(response.data)
    except Exception as e:
        print(f"Error getting posted images: {e}")
        return 0

def get_unposted_images():
    """Get images that haven't been posted yet"""
    if not supabase:
        return []
    try:
        response = supabase.table('images').select('*').execute()
        posted = supabase.table('feedback').select('image_id').execute()
        posted_ids = [p['image_id'] for p in posted.data]
        return [img for img in response.data if img['id'] not in posted_ids]
    except Exception as e:
        print(f"Error getting unposted images: {e}")
        return []

def auto_post():
    """Automatically post images based on schedule"""
    if get_posted_images_today() >= MAX_POSTS_PER_DAY:
        print("Daily post limit reached")
        return

    unposted = get_unposted_images()
    if not unposted:
        print("No unposted images available")
        return

    image = random.choice(unposted)
    # TODO: Implement actual Twitter posting
    print(f"Would post image {image['id']} to Twitter")

def run_scheduler():
    """Run the scheduler in a separate thread"""
    schedule.every(POSTING_INTERVAL_HOURS).hours.do(auto_post)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start scheduler in background thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

@app.get("/")
async def root():
    return {"message": "Marvin Social Agent is running"}

@app.get("/status")
async def status():
    return {
        "posted_today": get_posted_images_today(),
        "max_posts_per_day": MAX_POSTS_PER_DAY,
        "next_posting_time": schedule.next_run()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 