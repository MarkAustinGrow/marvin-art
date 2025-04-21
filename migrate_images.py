import os
from dotenv import load_dotenv
from supabase import create_client
import requests
from datetime import datetime
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment variables")
    exit(1)

try:
    supabase = create_client(
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    print("Successfully initialized Supabase client")
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}")
    exit(1)

def migrate_existing_images():
    """Migrate existing images to Supabase Storage"""
    try:
        # Get all images that don't have a storage_path
        response = supabase.table('images').select('id, image_url, local_path').is_('storage_path', 'null').execute()
        
        if not response.data:
            print("No images to migrate")
            return
        
        print(f"Found {len(response.data)} images to migrate")
        
        for image in response.data:
            try:
                image_id = image['id']
                local_path = image.get('local_path')
                
                # Try local file first
                if local_path and os.path.exists(local_path):
                    print(f"Migrating image {image_id} from local file: {local_path}")
                    
                    # Create storage path
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = os.path.basename(local_path)
                    storage_path = f"images/migrated/{timestamp}_{filename}"
                    
                    # Upload to storage
                    with open(local_path, 'rb') as f:
                        supabase.storage.from_("marvin-art-images").upload(
                            path=storage_path,
                            file=f,
                            file_options={"content-type": "image/png"}
                        )
                    
                    # Get permanent URL
                    permanent_url = supabase.storage.from_("marvin-art-images").get_public_url(storage_path)
                    
                    # Update database
                    supabase.table('images').update({
                        "storage_path": storage_path,
                        "dalle_url": image['image_url'],
                        "image_url": permanent_url
                    }).eq('id', image_id).execute()
                    
                    print(f"Successfully migrated image {image_id}")
                    
                # Try URL if local file doesn't exist
                elif image.get('image_url'):
                    try:
                        print(f"Migrating image {image_id} from URL")
                        
                        # Download image
                        response = requests.get(image['image_url'], timeout=5)
                        if response.status_code == 200:
                            # Create storage path
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"migrated_{timestamp}.png"
                            storage_path = f"images/migrated/{filename}"
                            
                            # Upload to storage
                            supabase.storage.from_("marvin-art-images").upload(
                                path=storage_path,
                                file=response.content,
                                file_options={"content-type": "image/png"}
                            )
                            
                            # Get permanent URL
                            permanent_url = supabase.storage.from_("marvin-art-images").get_public_url(storage_path)
                            
                            # Update database
                            supabase.table('images').update({
                                "storage_path": storage_path,
                                "dalle_url": image['image_url'],
                                "image_url": permanent_url
                            }).eq('id', image_id).execute()
                            
                            print(f"Successfully migrated image {image_id}")
                        else:
                            print(f"Failed to download image {image_id}: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"Error migrating image {image_id} from URL: {str(e)}")
                
                else:
                    print(f"No source available for image {image_id}")
            
            except Exception as e:
                print(f"Error migrating image {image_id}: {str(e)}")
    
    except Exception as e:
        print(f"Error in migration: {str(e)}")

if __name__ == "__main__":
    migrate_existing_images()
