# Marvin Art Generator

An AI-powered art generation system that creates unique artwork using DALL-E 3 and GPT-4. The system runs on a schedule, generating up to 2 images per day, and includes a FastAPI server for API access.

## Features

- Automatic art generation using DALL-E 3
- GPT-4 powered prompt generation
- Scheduled generation (2 images per day)
- FastAPI server for API access
- Supabase database integration
- Image tracking and management
- Social media posting integration

## Setup

1. Clone the repository:
```bash
git clone https://github.com/MarkAustinGrow/marvin-art.git
cd marvin-art
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_api_key
```

4. Run the server:
```bash
python marvin_art.py
```

## API Endpoints

- `GET /`: Check if the service is running
- `POST /generate`: Generate new art
- `GET /unposted`: Get images that haven't been posted yet

## Configuration

- `MAX_IMAGES_PER_DAY`: Maximum number of images to generate per day (default: 2)
- `GENERATION_INTERVAL_HOURS`: Hours between generations (default: 12)
- `CHARACTER_ID`: ID of the character in the database

## Database Schema

### Prompts Table
- `id`: UUID primary key
- `text`: The prompt text
- `character_id`: Reference to character
- `created_at`: Timestamp

### Images Table
- `id`: UUID primary key
- `prompt_id`: Reference to prompt
- `api_used`: AI art API used
- `image_url`: URL of generated image
- `local_path`: Local file path
- `settings`: Generation settings
- `created_at`: Timestamp

## License

MIT License 