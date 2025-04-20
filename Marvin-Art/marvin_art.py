import os
from supabase import create_client

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