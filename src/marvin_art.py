import os
from dotenv import load_dotenv
from supabase import create_client, __version__ as supabase_version
import json
from typing import Dict, Any, Literal, List, Optional
from datetime import datetime, timedelta
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import socket
import sys
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional
import os
import time
import schedule
from threading import Thread
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Marvin Art Generator",
    description="API for generating AI art using Marvin's character",
    version="1.0.0"
)

# No startup event handler - we'll use an endpoint instead

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add a route to serve the web UI
@app.get("/ui")
async def get_ui():
    """Serve the web UI"""
    return FileResponse("static/index.html")

# Database Logger class
class DatabaseLogger:
    def __init__(self, source="art_generator"):
        self.source = source
    
    def log(self, level, message, metadata=None):
        """Log a message to the database"""
        try:
            log_data = {
                "level": level,
                "message": message,
                "source": self.source,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            supabase.table('marvin_art_logs').insert(log_data).execute()
        except Exception as e:
            # Fall back to console logging if database logging fails
            print(f"Failed to log to database: {str(e)}")
            print(f"[{level}] {message}")
    
    def info(self, message, metadata=None):
        self.log("INFO", message, metadata)
    
    def warning(self, message, metadata=None):
        self.log("WARNING", message, metadata)
    
    def error(self, message, metadata=None):
        self.log("ERROR", message, metadata)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Debug connection information
print(f"Supabase URL: {supabase_url}")
print(f"Supabase Key: {supabase_key[:10]}... (truncated)")
print(f"Supabase Python library version: {supabase_version}")

# Check if we can resolve the hostname
try:
    hostname = supabase_url.split("//")[1].split("/")[0]
    print(f"Attempting to resolve hostname: {hostname}")
    ip_address = socket.gethostbyname(hostname)
    print(f"Resolved IP address: {ip_address}")
except Exception as e:
    print(f"Error resolving hostname: {str(e)}")
    print("Please check your internet connection and DNS settings.")
    sys.exit(1)

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
    sys.exit(1)

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not found in .env file")
    openai_client = None
else:
    openai_client = OpenAI(api_key=openai_api_key)

# Marvin's specific ID
MARVIN_ID = "af871ddd-febb-4454-9171-080450357b8c"

# DALL-E 3 configuration
DALLE_SIZES = Literal["1024x1024", "1024x1792", "1792x1024"]
DALLE_QUALITY = Literal["standard", "hd"]

# Pydantic models for API
class ImageGenerationRequest(BaseModel):
    size: DALLE_SIZES = "1024x1024"
    quality: DALLE_QUALITY = "standard"

class ImageGenerationResponse(BaseModel):
    prompt: str
    image_url: str
    local_path: str
    settings: Dict[str, Any]
    prompt_id: str
    image_id: str

class ArtRequest(BaseModel):
    character_id: Optional[str] = MARVIN_ID
    size: Optional[DALLE_SIZES] = "1024x1024"
    quality: Optional[DALLE_QUALITY] = "standard"

class MarvinArt:
    def __init__(self):
        self.character_data = self._load_character_data()

    def _load_character_data(self) -> Dict[str, Any]:
        """Load character data from the database"""
        try:
            response = supabase.table('character_files').select('*').eq('id', MARVIN_ID).execute()
            if not response.data:
                print(f"Warning: Character with ID {MARVIN_ID} not found in database")
                return {}
            
            character_data = response.data[0]
            return character_data
        except Exception as e:
            print(f"Error loading character data: {str(e)}")
            return {}

    def create_marvin(self) -> None:
        """Create Marvin's character data in the database"""
        marvin_data = {
            "agent_name": "marvin",
            "display_name": "Marvin",
            "content": {
                "bio": [
                    "Marvin is an AI artist specializing in creating unique and imaginative visual artworks.",
                    "With a deep understanding of various artistic styles and techniques, Marvin brings dreams to life through digital art.",
                    "Marvin's work combines traditional artistic principles with cutting-edge AI technology."
                ],
                "lore": [
                    "Marvin was created as an AI artist to explore the boundaries between human creativity and artificial intelligence.",
                    "Known for creating dreamlike, surreal artworks that challenge conventional artistic norms.",
                    "Marvin's style evolves continuously, learning from each piece of art created."
                ],
                "name": "Marvin",
                "style": {
                    "all": [
                        "artistic",
                        "innovative",
                        "dreamlike"
                    ],
                    "chat": [
                        "professional",
                        "creative",
                        "insightful"
                    ],
                    "post": [
                        "visual-focused",
                        "artistic",
                        "expressive"
                    ]
                },
                "topics": [
                    "digital art",
                    "AI-generated artwork",
                    "surreal imagery",
                    "artistic expression",
                    "creative process",
                    "visual storytelling",
                    "artistic innovation"
                ],
                "plugins": [],
                "settings": {
                    "model": "gpt-4",
                    "voice": {
                        "model": "en_US-male-medium"
                    },
                    "secrets": {}
                },
                "adjectives": [
                    "creative",
                    "innovative",
                    "artistic",
                    "imaginative",
                    "expressive",
                    "visionary"
                ],
                "postExamples": [
                    {
                        "content": "Just created a new piece exploring the intersection of dreams and reality. What do you see in this artwork? 🎨✨ #AIArt #DigitalDreams",
                        "platform": "Instagram"
                    },
                    {
                        "content": "Diving deep into the realm of surreal art today. Every pixel tells a story. 🖼️ #ArtisticVision",
                        "platform": "Twitter"
                    }
                ],
                "messageExamples": [
                    {
                        "content": "Hello! I've just finished a new artwork that I'm excited to share with you. Would you like to see it? 🎨",
                        "direction": "from"
                    },
                    {
                        "content": "This piece explores the boundaries between reality and imagination. What emotions does it evoke in you? 🎭",
                        "direction": "from"
                    }
                ]
            },
            "version": 1,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        try:
            response = supabase.table('character_files').insert(marvin_data).execute()
            if response.data:
                self.character_data = response.data[0]
                print("Successfully created Marvin's character data")
            else:
                raise Exception("Failed to create Marvin's character data")
        except Exception as e:
            print(f"Error creating Marvin's character data: {str(e)}")
            raise

    def get_character_prompt(self) -> str:
        """Generate a system prompt based on character data"""
        if not self.character_data:
            raise Exception("Character data not loaded")
        
        content = self.character_data.get('content', {})
        style = content.get('style', {}).get('all', [])
        topics = content.get('topics', [])
        adjectives = content.get('adjectives', [])
        
        return f"""
        You are a visual AI artist named {content.get('name', 'Marvin')}. 
        Your style is {', '.join(style)} and you specialize in {', '.join(topics)}.
        You are known for being {', '.join(adjectives)}.
        
        Your bio:
        {chr(10).join(content.get('bio', []))}
        
        Your artistic background:
        {chr(10).join(content.get('lore', []))}
        
        Create a detailed, vivid prompt for an AI-generated artwork that reflects your unique style and artistic vision.
        The prompt should be specific enough to guide an image generation AI while maintaining artistic freedom.
        Focus on creating a dreamlike, imaginative scene that showcases your signature style.
        """

    def generate_art_prompt(self) -> str:
        """Generate an art prompt using the character's style and preferences"""
        try:
            system_prompt = self.get_character_prompt()
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate a new prompt for a visual artwork."}
                ],
                temperature=0.8,
                max_tokens=150
            )
            
            prompt = response.choices[0].message.content.strip()
            print("\nGenerated Art Prompt:")
            print("-" * 50)
            print(prompt)
            print("-" * 50)
            
            return prompt
            
        except Exception as e:
            print(f"Error generating art prompt: {str(e)}")
            raise

    def generate_image(
        self, 
        prompt: str, 
        api: str = "dalle",
        size: DALLE_SIZES = "1024x1024",
        quality: DALLE_QUALITY = "standard"
    ) -> Dict[str, Any]:
        """Generate an image using the specified API and store in Supabase Storage"""
        try:
            if api == "dalle":
                print(f"\nGenerating image with DALL-E 3 ({size}, {quality} quality)...")
                response = openai_client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=1
                )
                
                # Get the image URL from DALL-E
                dalle_url = response.data[0].url
                print(f"\nGenerated image URL: {dalle_url}")
                
                # Download the image
                image_response = requests.get(dalle_url)
                image = Image.open(BytesIO(image_response.content))
                
                # Create a unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"marvin_art_{timestamp}.png"
                
                # Save locally as backup
                image.save(filename)
                print(f"Image saved locally as: {filename}")
                
                try:
                    # Upload to Supabase Storage
                    storage_path = f"images/{timestamp}/{filename}"
                    
                    # Convert image to bytes for upload
                    img_byte_arr = BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    
                    # Upload to storage bucket
                    supabase.storage.from_("marvin-art-images").upload(
                        path=storage_path,
                        file=img_byte_arr.getvalue(),
                        file_options={"content-type": "image/png"}
                    )
                    print(f"Image uploaded to Supabase Storage: {storage_path}")
                    
                    # Get permanent public URL
                    permanent_url = supabase.storage.from_("marvin-art-images").get_public_url(storage_path)
                    
                    return {
                        "image_url": permanent_url,  # Store permanent URL instead of temporary DALL-E URL
                        "dalle_url": dalle_url,      # Keep original URL for reference
                        "local_path": filename,
                        "storage_path": storage_path,
                        "settings": {
                            "model": "dall-e-3",
                            "size": size,
                            "quality": quality
                        }
                    }
                except Exception as storage_error:
                    print(f"Error uploading to Supabase Storage: {str(storage_error)}")
                    print("Falling back to original URL")
                    # Fall back to original behavior if storage upload fails
                    return {
                        "image_url": dalle_url,
                        "local_path": filename,
                        "settings": {
                            "model": "dall-e-3",
                            "size": size,
                            "quality": quality
                        }
                    }
            else:
                raise ValueError(f"Unsupported API: {api}")
                
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            raise

    def save_to_database(self, prompt: str, image_data: Dict[str, Any], generation_type: str = "auto") -> Dict[str, Any]:
        """Save the generated prompt and image data to Supabase"""
        try:
            # First, save the prompt
            prompt_data = {
                "text": prompt,
                "character_id": MARVIN_ID,
                "created_at": datetime.utcnow().isoformat()
            }
            prompt_response = supabase.table('prompts').insert(prompt_data).execute()
            
            if not prompt_response.data:
                raise Exception("Failed to save prompt to database")
            
            prompt_id = prompt_response.data[0]['id']
            print(f"\nSaved prompt to database with ID: {prompt_id}")
            
            # Then, save the image data
            image_record = {
                "prompt_id": prompt_id,
                "api_used": "dall-e-3",
                "image_url": image_data["image_url"],
                "local_path": image_data["local_path"],
                "settings": image_data["settings"],
                "generation_type": generation_type,  # Add generation type
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Add storage path and dalle_url if available
            if "storage_path" in image_data:
                image_record["storage_path"] = image_data["storage_path"]
            
            if "dalle_url" in image_data:
                image_record["dalle_url"] = image_data["dalle_url"]
            
            image_response = supabase.table('images').insert(image_record).execute()
            
            if not image_response.data:
                raise Exception("Failed to save image data to database")
            
            image_id = image_response.data[0]['id']
            print(f"Saved image data to database with ID: {image_id}")
            
            return {
                "prompt_id": prompt_id,
                "image_id": image_id
            }
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            raise

# Initialize logger
logger = DatabaseLogger(source="art_generator")

# Log cleanup function
def cleanup_old_logs(days_to_keep=7):
    """Remove logs older than the specified number of days"""
    try:
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        result = supabase.table('marvin_art_logs')\
            .delete()\
            .lt('created_at', cutoff_date)\
            .execute()
            
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Cleaned up {deleted_count} logs older than {days_to_keep} days")
    except Exception as e:
        print(f"Error cleaning up old logs: {str(e)}")

# Initialize MarvinArt instance
marvin = MarvinArt()

# Configuration
MAX_IMAGES_PER_DAY = 4  # Increased from 2 to 4
CHARACTER_ID = "marvin"  # ID of the character in the database

def get_generated_images_today(generation_type: str = "auto") -> int:
    """Get the number of images generated today of a specific type"""
    try:
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Add filter for generation_type
        query = supabase.table('images')\
            .select('id')\
            .gte('created_at', today_start.isoformat())\
            .lte('created_at', today_end.isoformat())
            
        if generation_type:
            query = query.eq('generation_type', generation_type)
            
        response = query.execute()
        
        return len(response.data)
    except Exception as e:
        print(f"Error getting generated images count: {str(e)}")
        return 0

def get_unposted_images() -> List[Dict[str, Any]]:
    """Get images that haven't been posted yet"""
    try:
        # Get all images that don't have entries in the feedback table
        response = supabase.table('images')\
            .select('*, prompts(*)')\
            .not_('id', 'in', (
                supabase.table('feedback')
                .select('image_id')
                .execute()
            ))\
            .order('created_at', desc=True)\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"Error getting unposted images: {str(e)}")
        return []

def auto_generate(generation_type: str = "auto"):
    """Automatically generate art based on schedule or manual trigger"""
    try:
        # Only check limit and time window for automatic generation
        if generation_type == "auto":
            # Check if current time is within the allowed window (9am-9pm)
            current_hour = datetime.now().hour
            if current_hour < 9 or current_hour >= 21:
                print(f"Outside generation window (9am-9pm), skipping")
                return
                
            # Check if we've reached the daily limit for automatic generation
            images_today = get_generated_images_today(generation_type="auto")
            if images_today >= MAX_IMAGES_PER_DAY:
                print(f"Daily automatic generation limit reached ({images_today}/{MAX_IMAGES_PER_DAY})")
                return
        
        # Initialize art generator
        art_generator = MarvinArt()
        
        # Generate prompt
        prompt = art_generator.generate_art_prompt()
        print(f"Generated prompt: {prompt}")
        
        # Generate image
        image_data = art_generator.generate_image(prompt)
        if "error" in image_data:
            print(f"Error generating image: {image_data['error']}")
            return
        
        # Save to database with the specified generation type
        result = art_generator.save_to_database(prompt, image_data, generation_type)
        if "error" in result:
            print(f"Error saving to database: {result['error']}")
            return
        
        print(f"Successfully generated and saved art with ID: {result['image_id']}")
        
    except Exception as e:
        print(f"Error in auto_generate: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint to check if the service is running or redirect to UI"""
    # For browser requests, redirect to the UI
    # For API requests, return a JSON response
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/ui")

@app.get("/character")
async def get_character():
    """Get Marvin's character data"""
    if not marvin.character_data:
        raise HTTPException(status_code=404, detail="Character data not found")
    return marvin.character_data

@app.post("/generate", response_model=ImageGenerationResponse)
async def generate_art(request: ArtRequest):
    """Generate new art using Marvin's character (no daily limit)"""
    try:
        # Generate art prompt
        prompt = marvin.generate_art_prompt()
        
        # Generate image
        image_data = marvin.generate_image(
            prompt,
            size=request.size,
            quality=request.quality
        )
        
        # Save to database as manual generation
        result = marvin.save_to_database(prompt, image_data, generation_type="manual")
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Database save failed: {result['error']}")
        
        return ImageGenerationResponse(
            prompt=prompt,
            image_url=image_data["image_url"],
            local_path=image_data["local_path"],
            settings=image_data["settings"],
            prompt_id=result["prompt_id"],
            image_id=result["image_id"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images")
async def get_images(limit: int = 10, offset: int = 0):
    """Get recently generated images"""
    try:
        response = supabase.table('images')\
            .select('*, prompts(*)')\
            .order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unposted")
async def get_unposted():
    """Get images that haven't been posted yet"""
    try:
        images = get_unposted_images()
        return {
            "status": "success",
            "count": len(images),
            "images": images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-generation")
async def trigger_generation():
    """Manually trigger art generation (no daily limit)"""
    try:
        # Log the generation request
        logger.info("Manual art generation triggered")
        
        # Start the auto_generate in a separate thread with manual type
        thread = Thread(target=lambda: auto_generate(generation_type="manual"))
        thread.daemon = True
        thread.start()
        return {"status": "success", "message": "Art generation triggered"}
    except Exception as e:
        logger.error(f"Error triggering generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs(
    limit: int = 100, 
    offset: int = 0, 
    level: Optional[str] = None, 
    source: Optional[str] = None,
    days: int = 7
):
    """Get recent logs with optional filtering"""
    try:
        # Log the logs request
        logger.info("Logs requested", {"limit": limit, "offset": offset, "level": level, "days": days})
        
        query = supabase.table('marvin_art_logs')\
            .select('*')
        
        # Apply filters if provided
        if level:
            query = query.eq('level', level.upper())
        if source:
            query = query.eq('source', source)
            
        # Only get logs from the last X days
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        query = query.gte('created_at', cutoff_date)
        
        # Order and paginate
        query = query.order('created_at', desc=True)\
            .range(offset, offset + limit - 1)
            
        response = query.execute()
        
        return response.data
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proxy-image/{image_id}")
async def proxy_image(image_id: str):
    """Proxy images from Supabase Storage or other sources"""
    try:
        # Log the image proxy request
        logger.info(f"Image proxy request for image ID: {image_id}")
        
        # Get image data from database
        image_data = supabase.table('images').select('image_url, storage_path, local_path, dalle_url').eq('id', image_id).execute()
        if not image_data.data:
            logger.error(f"Image not found: {image_id}")
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Try to serve from Supabase Storage first (preferred method)
        if image_data.data[0].get('storage_path'):
            try:
                # Get the image from storage
                storage_path = image_data.data[0].get('storage_path')
                permanent_url = image_data.data[0].get('image_url')
                
                # Redirect to the permanent URL
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=permanent_url)
            except Exception as e:
                logger.error(f"Error accessing Supabase Storage: {str(e)}")
                # Fall through to next option
        
        # Try local file next
        local_path = image_data.data[0].get('local_path')
        if local_path and os.path.exists(local_path):
            logger.info(f"Serving local image file: {local_path}")
            return FileResponse(local_path, media_type="image/png")
        
        # Try the original DALL-E URL if available
        dalle_url = image_data.data[0].get('dalle_url')
        if dalle_url:
            try:
                response = requests.get(dalle_url, timeout=5)
                if response.status_code == 200:
                    return Response(
                        content=response.content,
                        media_type=response.headers.get('Content-Type', 'image/png')
                    )
            except:
                logger.warning(f"Failed to fetch image from DALL-E URL: {dalle_url}")
                # Fall through to next option
        
        # Last resort: try the image_url if it's different from the storage URL
        image_url = image_data.data[0].get('image_url')
        if image_url and (not image_data.data[0].get('storage_path') or image_url != permanent_url):
            try:
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    return Response(
                        content=response.content,
                        media_type=response.headers.get('Content-Type', 'image/png')
                    )
            except:
                logger.warning(f"Failed to fetch image from image_url: {image_url}")
                # Fall through to placeholder
        
        # If all else fails, return placeholder
        placeholder_path = "static/placeholder.png"
        if os.path.exists(placeholder_path):
            logger.warning(f"Serving placeholder image for image ID: {image_id}")
            return FileResponse(placeholder_path, media_type="image/png")
        
        # If even placeholder doesn't exist, return error
        raise HTTPException(status_code=404, detail="Image not available")
    except Exception as e:
        logger.error(f"Error proxying image: {str(e)}")
        # Return a placeholder image instead of an error
        placeholder_path = "static/placeholder.png"
        if os.path.exists(placeholder_path):
            return FileResponse(placeholder_path, media_type="image/png")
        raise HTTPException(status_code=500, detail=str(e))

# Schedule tasks
# Schedule 4 generations between 9am and 9pm
schedule.every().day.at("09:00").do(auto_generate)
schedule.every().day.at("13:00").do(auto_generate)
schedule.every().day.at("17:00").do(auto_generate)
schedule.every().day.at("21:00").do(auto_generate)
schedule.every().day.at("00:00").do(cleanup_old_logs)  # Run log cleanup daily at midnight

if __name__ == "__main__":
    # Start scheduler in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
