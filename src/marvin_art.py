import os
from dotenv import load_dotenv
from supabase import create_client, __version__ as supabase_version
import json
from typing import Dict, Any, Literal, List, Optional
from datetime import datetime
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import socket
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
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

# Add startup event handler
@app.on_startup
async def startup_event():
    """Run tasks when the server starts up"""
    print("Server started, running startup tasks...")
    # Start the auto_generate in a separate thread to avoid blocking startup
    Thread(target=auto_generate).start()

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
        """Generate an image using the specified API"""
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
                
                # Get the image URL
                image_url = response.data[0].url
                print(f"\nGenerated image URL: {image_url}")
                
                # Download and save the image
                image_response = requests.get(image_url)
                image = Image.open(BytesIO(image_response.content))
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"marvin_art_{timestamp}.png"
                image.save(filename)
                print(f"Image saved as: {filename}")
                
                return {
                    "image_url": image_url,
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

    def save_to_database(self, prompt: str, image_data: Dict[str, Any]) -> Dict[str, Any]:
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
                "created_at": datetime.utcnow().isoformat()
            }
            
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

# Initialize MarvinArt instance
marvin = MarvinArt()

# Configuration
MAX_IMAGES_PER_DAY = 2
GENERATION_INTERVAL_HOURS = 12  # Space generations evenly throughout the day
CHARACTER_ID = "marvin"  # ID of the character in the database

def get_generated_images_today() -> int:
    """Get the number of images generated today"""
    try:
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        response = supabase.table('images')\
            .select('id')\
            .gte('created_at', today_start.isoformat())\
            .lte('created_at', today_end.isoformat())\
            .execute()
        
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

def auto_generate():
    """Automatically generate art based on schedule"""
    try:
        # Check if we've reached the daily limit
        images_today = get_generated_images_today()
        if images_today >= MAX_IMAGES_PER_DAY:
            print(f"Daily generation limit reached ({images_today}/{MAX_IMAGES_PER_DAY})")
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
        
        # Save to database
        result = art_generator.save_to_database(prompt, image_data)
        if "error" in result:
            print(f"Error saving to database: {result['error']}")
            return
        
        print(f"Successfully generated and saved art with ID: {result['image_id']}")
        
    except Exception as e:
        print(f"Error in auto_generate: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint to check if the service is running"""
    return {"status": "online", "service": "Marvin Art Generator"}

@app.get("/character")
async def get_character():
    """Get Marvin's character data"""
    if not marvin.character_data:
        raise HTTPException(status_code=404, detail="Character data not found")
    return marvin.character_data

@app.post("/generate", response_model=ImageGenerationResponse)
async def generate_art(request: ArtRequest):
    """Generate new art using Marvin's character"""
    try:
        # Check if we've reached the daily limit
        images_today = get_generated_images_today()
        if images_today >= MAX_IMAGES_PER_DAY:
            raise HTTPException(status_code=429, detail=f"Daily generation limit reached ({images_today}/{MAX_IMAGES_PER_DAY})")
        
        # Generate art prompt
        prompt = marvin.generate_art_prompt()
        
        # Generate image
        image_data = marvin.generate_image(
            prompt,
            size=request.size,
            quality=request.quality
        )
        
        # Save to database
        result = marvin.save_to_database(prompt, image_data)
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

# Schedule tasks
schedule.every(GENERATION_INTERVAL_HOURS).hours.do(auto_generate)

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
