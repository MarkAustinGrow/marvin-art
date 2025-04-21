# Marvin Art Generator System Documentation

## System Overview

The Marvin Art Generator is a distributed system that generates AI art using character-based prompts and manages social media interactions. The system consists of two main components:

1. **Marvin Art Generator** (`marvin_art.py`)
   - Generates art prompts using GPT-4
   - Creates images using DALL-E 3
   - Stores prompts and images in Supabase
   - Runs on port 8000

2. **Social Media Agent** (`social_agent.py`)
   - Manages social media posting
   - Collects and analyzes feedback
   - Runs on port 8001

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
  - `image_url` (text): URL of the generated image
  - `local_path` (text): Local storage path
  - `settings` (jsonb): Generation settings
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

## Component Details

### Marvin Art Generator

The art generator is responsible for:
1. Loading character data from Supabase
2. Generating art prompts using GPT-4
3. Creating images using DALL-E 3
4. Storing prompts and images in the database

Key classes:
- `MarvinArt`: Main class handling art generation
- `ImageGenerationRequest`: API request model
- `ImageGenerationResponse`: API response model
- `ArtRequest`: Art generation request model

### Social Media Agent

The social media agent handles:
1. Automated posting of generated images
2. Collection of engagement metrics
3. Sentiment analysis of feedback
4. Storage of feedback data

Key features:
- Maximum 2 posts per day
- 12-hour interval between posts
- Random selection of unposted images
- Feedback collection and analysis

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
│   └── requirements.txt  # Dependencies
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

- `POST /generate`: Generate new art
  - Request: `ArtRequest`
  - Response: `ImageGenerationResponse`

### Social Media Agent (Port 8001)

- `POST /post`: Create a new social media post
- `GET /feedback`: Retrieve feedback metrics
- `POST /feedback`: Submit new feedback

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
   docker logs marvin_marvin-social_1
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
