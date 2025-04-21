#!/bin/bash

# Stop any running containers
echo "Stopping any running containers..."
docker-compose down

# Start the container with the debug configuration
echo "Starting container with debug configuration..."
docker-compose -f docker-compose.debug.yml up -d

# Wait for the container to start
echo "Waiting for container to start..."
sleep 5

# Get the container ID
CONTAINER_ID=$(docker ps -q --filter "name=marvin_marvin-art")

if [ -z "$CONTAINER_ID" ]; then
  echo "Error: Container did not start properly."
  exit 1
fi

echo "Container started with ID: $CONTAINER_ID"
echo ""
echo "=== Environment Variables ==="
docker exec $CONTAINER_ID env | grep SUPABASE
docker exec $CONTAINER_ID env | grep OPENAI
echo ""

echo "=== Checking Database Tables ==="
docker exec $CONTAINER_ID python -c "
import os
from supabase import create_client

try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print('Error: SUPABASE_URL or SUPABASE_KEY environment variables are not set')
        exit(1)
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Check if the tables exist
    tables = ['character_files', 'prompts', 'images', 'feedback']
    for table in tables:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f'Table {table}: OK')
        except Exception as e:
            print(f'Table {table}: ERROR - {str(e)}')
except Exception as e:
    print(f'Error connecting to Supabase: {str(e)}')
"

echo ""
echo "=== Checking OpenAI API Key ==="
docker exec $CONTAINER_ID python -c "
import os
from openai import OpenAI

try:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print('Error: OPENAI_API_KEY environment variable is not set')
        exit(1)
    
    client = OpenAI(api_key=openai_api_key)
    
    # Make a simple API call to check if the key is valid
    response = client.models.list()
    print('OpenAI API Key: Valid')
except Exception as e:
    print(f'OpenAI API Key: ERROR - {str(e)}')
"

echo ""
echo "=== Manual Debugging Instructions ==="
echo "To connect to the container and run the script manually:"
echo "docker exec -it $CONTAINER_ID /bin/bash"
echo ""
echo "Inside the container, run:"
echo "python marvin_art.py"
echo ""
echo "This will show the full error message if the script crashes."
echo ""
echo "When you're done debugging, stop the container with:"
echo "docker-compose -f docker-compose.debug.yml down"
