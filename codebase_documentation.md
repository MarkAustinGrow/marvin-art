# Marvin Art Generator System Documentation

## System Overview

The Marvin Art Generator is a system that generates AI art using character-based prompts. The system consists of three main components:

1. **Marvin Art Generator** (`marvin_art.py`)
   - Generates art prompts using GPT-4
   - Creates images using DALL-E 3
   - Stores prompts and images in Supabase
   - Runs on port 8000

2. **Web Interface** (`static/`)
   - User-friendly interface for viewing and generating art
   - Gallery view of all generated images
   - Detailed image information display
   - Responsive design for all devices

3. **Logging System**
   - Records application events and errors
   - Stores logs in Supabase database
   - Provides API access to log data
   - Automatic log cleanup for maintenance

## Database Schema

The system uses Supabase with the following tables:

### character_files
- Stores character definitions and personalities
- Used for generating consistent art prompts
- Fields:
  - `id` (UUID): Primary key
  - `agent_name` (text): Character name
  - `display_name` (text): Display name
  - `content` (jsonb): Character configuration
  - `version` (int4): Version number
  - `is_active` (bool): Active status
  - `created_at` (timestamp): Creation timestamp
  - `updated_at` (timestamp): Update timestamp

### prompts
- Stores generated art prompts
- Links prompts to characters
- Fields:
  - `id` (UUID): Primary key
  - `text` (text): The prompt text
  - `character_id` (UUID): Reference to character_files table
  - `created_at` (timestamp): Creation timestamp

### images
- Stores generated images and metadata
- Links images to prompts
- Fields:
  - `id` (UUID): Primary key
  - `prompt_id` (UUID): Reference to prompts table
  - `api_used` (text): The AI art API used (e.g., "dalle")
  - `image_url` (text): URL of the generated image (Supabase Storage URL)
  - `local_path` (text): Local storage path
  - `storage_path` (varchar): Path in Supabase Storage bucket
  - `dalle_url` (text): Original DALL-E URL (temporary)
  - `settings` (jsonb): Generation settings
  - `generation_type` (text): Type of generation ("auto" or "manual")
  - `created_at` (timestamp): Creation timestamp

### feedback
- Stores social media engagement metrics
- Links feedback to images
- Fields:
  - `id` (UUID): Primary key
  - `image_id` (UUID): Reference to images table
  - `platform` (text): Social media platform
  - `engagement_score` (float): Engagement metric
  - `sentiment_score` (float): Sentiment analysis score
  - `collected_at` (timestamp): Collection timestamp

### marvin_art_logs
- Stores application logs and events
- Provides audit trail and debugging information
- Fields:
  - `id` (UUID): Primary key
  - `level` (varchar): Log level (INFO, WARNING, ERROR)
  - `message` (text): Log message content
  - `source` (varchar): Source of the log entry
  - `created_at` (timestamp): Creation timestamp
  - `metadata` (jsonb): Additional contextual data

## Component Details

### Marvin Art Generator

The art generator is responsible for:
1. Loading character data from Supabase
2. Generating art prompts using GPT-4
3. Creating images using DALL-E 3
4. Storing images in Supabase Storage
5. Storing prompts and image metadata in the database

Key classes:
- `MarvinArt`: Main class handling art generation
- `ImageGenerationRequest`: API request model
- `ImageGenerationResponse`: API response model
- `ArtRequest`: Art generation request model

#### Generation Types and Limits

The system supports two types of image generation:

1. **Automatic Generation** (`generation_type = "auto"`)
   - Scheduled generation that runs automatically
   - Limited to 2 images per day
   - Runs at 12-hour intervals

2. **Manual Generation** (`generation_type = "manual"`)
   - Triggered by user through the web interface
   - No daily limit
   - Available on-demand

#### Image Storage System

The system uses a multi-layered approach to ensure images remain accessible:

1. **Supabase Storage**
   - Primary storage for all generated images
   - Images are stored in a public bucket named "marvin-art-images"
   - Organized in folders by timestamp
   - Provides permanent URLs that don't expire

2. **Local File Storage**
   - Secondary backup of images on the server
   - Used as fallback if Supabase Storage is unavailable

3. **Original DALL-E URLs**
   - Stored as reference but not relied upon
   - These URLs expire after a few hours

4. **Placeholder Image**
   - Used when no other image source is available
   - Prevents broken images in the UI

### Web Interface

The web interface provides a user-friendly way to interact with the Marvin Art Generator:

1. **Gallery View**
   - Displays all generated images in a responsive grid
   - Shows image prompts and generation dates
   - Supports lazy loading for performance

2. **Image Details**
   - Modal view with full-size image
   - Complete prompt text
   - Generation settings and metadata
   - Option to open image in new tab

3. **Generation Controls**
   - "Generate New Art" button to trigger manual generation
   - Status indicators for generation process
   - Auto-refresh when new images are available


### Logging System

The logging system is responsible for:
1. Capturing application events, warnings, and errors
2. Storing log entries in the Supabase database
3. Providing API access to log data
4. Automatic cleanup of old log entries

Key classes:
- `DatabaseLogger`: Main class handling log storage and retrieval
  - Methods: `info()`, `warning()`, `error()`, `log()`
  - Supports metadata for additional context

#### Log Levels

The system supports three log levels:

1. **INFO**
   - Normal operational messages
   - System status updates
   - Non-critical events

2. **WARNING**
   - Potential issues that don't prevent operation
   - Resource limitations
   - Degraded performance conditions

3. **ERROR**
   - Critical issues that prevent normal operation
   - API failures
   - Database connection problems

#### Log Maintenance

The system includes automatic log maintenance:
- Logs older than 7 days are automatically deleted
- Cleanup runs daily at midnight
- Prevents database bloat and maintains performance

## Environment Configuration

The system requires the following environment variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

## Project Structure

The project is organized as follows:

```
Marvin-Art/
├── src/                  # Source code directory
│   ├── marvin_art.py     # Art Generator code
│   ├── requirements.txt  # Dependencies
│   └── static/           # Web interface files
│       ├── index.html    # Main HTML file
│       ├── styles.css    # CSS styles
│       └── script.js     # JavaScript functionality
├── docker/               # Docker-related files
│   └── Dockerfile        # Dockerfile for the Art Generator
├── docker-compose.yml    # Docker Compose configuration
└── docker-compose.debug.yml # Debug configuration
```

## Docker Deployment

The system is containerized using Docker:

1. **Marvin Art Generator Container**
   - Port: 8000
   - Environment: Python 3.8
   - Dependencies: Listed in `src/requirements.txt`

## API Endpoints

### Marvin Art Generator (Port 8000)

#### API Endpoints
- `GET /`: Redirects to the web UI
- `GET /ui`: Serves the web interface
- `GET /character`: Get Marvin's character data
- `POST /generate`: Generate new art (no daily limit)
  - Request: `ArtRequest`
  - Response: `ImageGenerationResponse`
- `GET /images`: Get recently generated images
  - Query params: `limit` (default: 10), `offset` (default: 0)
- `GET /unposted`: Get images that haven't been posted yet
- `POST /trigger-generation`: Manually trigger art generation (no daily limit)
- `GET /proxy-image/{image_id}`: Serve images with fallback mechanisms
  - Tries Supabase Storage, local files, and original URLs
  - Falls back to placeholder image if all sources fail
- `GET /logs`: Retrieve application logs
  - Query params: 
    - `limit` (default: 100): Maximum number of logs to return
    - `offset` (default: 0): Pagination offset
    - `level` (optional): Filter by log level (INFO, WARNING, ERROR)
    - `source` (optional): Filter by log source
    - `days` (default: 7): Only return logs from the last X days

#### Static Files
- `/static/*`: Serves static files for the web interface


## Web Interface Usage

The web interface is accessible at `http://your-server-ip:8000/` or your configured domain name.

### Features:

1. **Viewing Images**
   - The gallery displays the most recent images
   - Click on any image to view details
   - Images load with a fade-in animation

2. **Generating Images**
   - Click the "Generate New Art" button
   - The system will show a loading indicator
   - Once complete, the new image will appear in the gallery

3. **Image Details**
   - Click any image to open the details modal
   - View the full prompt text
   - See generation settings and date
   - Open the full image in a new tab

## Database Migration

### Adding Generation Type

If you need to add the `generation_type` column to your database, run the following SQL:

```sql
-- Add generation_type column to images table
ALTER TABLE images 
ADD COLUMN generation_type VARCHAR(10) DEFAULT 'auto' NOT NULL;

-- Update existing records to have 'auto' as their generation type
UPDATE images SET generation_type = 'auto';
```

### Adding Storage Columns

To add Supabase Storage support, run the following SQL:

```sql
-- Add storage_path column to images table
ALTER TABLE images 
ADD COLUMN storage_path VARCHAR(255);

-- Add dalle_url column to store the original URL
ALTER TABLE images 
ADD COLUMN dalle_url TEXT;
```

### Migrating Existing Images

To migrate existing images to Supabase Storage, use the `migrate_images.py` script:

```bash
# On your local machine
python migrate_images.py

# On the server (if Python 3 is the default)
python3 migrate_images.py
```

This script will:
1. Find all images without a storage_path
2. Try to upload them to Supabase Storage from local files
3. If local files aren't available, try to download from the original URL
4. Update the database with the new storage_path and permanent URL

## Development Guidelines

1. **Code Organization**
   - Follow SOLID principles
   - Maintain single responsibility for each module
   - Use interfaces for abstraction
   - Keep code DRY (Don't Repeat Yourself)

2. **Testing**
   - Write unit tests for each module
   - Test API endpoints
   - Validate database operations
   - Check error handling

3. **Documentation**
   - Document all classes and methods
   - Include usage examples
   - Keep README up to date
   - Document API changes

4. **Error Handling**
   - Implement proper error handling
   - Log errors appropriately
   - Provide meaningful error messages
   - Handle edge cases

5. **Logging Best Practices**
   - Use appropriate log levels (INFO, WARNING, ERROR)
   - Include relevant context in log messages
   - Add metadata for structured information
   - Don't log sensitive information
   - Use source parameter to identify the component

## Deployment Process

1. Update code in GitHub repository
2. Pull changes on server:
   ```bash
   git pull origin master
   ```
3. Rebuild and restart containers:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```
4. Monitor logs for any issues:
   ```bash
   docker logs marvin_marvin-art_1
   ```

## Monitoring and Maintenance

1. **Logs**
   - Check container logs regularly
   - Monitor for errors and warnings
   - Track API usage and performance

2. **Database**
   - Monitor table sizes
   - Check for data consistency
   - Perform regular backups

3. **Performance**
   - Monitor API response times
   - Track resource usage
   - Optimize as needed

4. **Security**
   - Keep dependencies updated
   - Monitor for security issues
   - Follow security best practices

5. **Logs**
   - Monitor logs for errors and warnings
   - Use the `/logs` endpoint to view recent logs
   - Check log volume for unusual activity
   - Logs are automatically cleaned up after 7 days

## Troubleshooting

### Common Issues

1. **Database Schema Errors**
   - If you see errors about missing columns, run the database migration script
   - Check Supabase dashboard for table structure

2. **Image Generation Failures**
   - Verify OpenAI API key is valid
   - Check OpenAI API usage limits
   - Ensure proper network connectivity

3. **Web Interface Issues**
   - Clear browser cache
   - Check browser console for JavaScript errors
   - Verify static files are being served correctly

4. **Logging Issues**
   - If logs aren't being saved, check Supabase connection
   - Verify the `marvin_art_logs` table exists
   - Check for errors in the console output
   - Use the `/logs` endpoint to view recent logs

5. **Image Loading Issues**
   - If images aren't displaying, check the browser console for errors
   - Verify the Supabase Storage bucket is set to public
   - Check if the proxy endpoint is working correctly
   - Ensure the placeholder image exists at `static/placeholder.png`
   - Check if the image exists in Supabase Storage using the dashboard

6. **Supabase Storage Issues**
   - Verify your Supabase API key has storage permissions
   - Check if the "marvin-art-images" bucket exists and is public
   - Ensure you have sufficient storage quota
   - Check network connectivity to Supabase
