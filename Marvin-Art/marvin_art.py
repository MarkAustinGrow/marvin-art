import os
from dotenv import load_dotenv
from supabase import create_client, Client
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

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment variables")
    sys.exit(1)

# Debug connection information
print(f"Supabase URL: {supabase_url}")
print(f"Supabase Key: {supabase_key[:10]}... (truncated)")

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
    # Initialize Supabase client with project URL and key
    supabase = create_client(
        supabase_url,
        supabase_key
    )
    print("Successfully initialized Supabase client")
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}")
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
            return response.data[0]
        except Exception as e:
            print(f"Error loading character data: {str(e)}")
            return {} 