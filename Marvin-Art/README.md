# Marvin Art Generator

An AI-powered art generation system that creates unique artwork using GPT-4 for prompt generation and DALL-E 3 for image creation.

## Features

- GPT-4 powered art prompt generation
- DALL-E 3 image generation with multiple size options
- Automatic image saving with timestamps
- Supabase database integration for storing prompts and images
- Docker support for easy deployment

## Prerequisites

- Python 3.8+
- OpenAI API key
- Supabase account and credentials
- Docker and Docker Compose (optional)

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/MarkAustinGrow/marvin-art.git
cd marvin-art
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your credentials:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### Docker Setup

1. Clone the repository:
```bash
git clone https://github.com/MarkAustinGrow/marvin-art.git
cd marvin-art
```

2. Create a `.env` file with your credentials:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Usage

### Local Usage

Run the script:
```bash
python marvin_art.py
```

### Docker Usage

The application will automatically run when started with Docker Compose. To stop it:
```bash
docker-compose down
```

## Database Setup

1. Create the required tables in your Supabase database using the provided SQL script:
```sql
-- Run the contents of create_ai_art_tables.sql in your Supabase SQL editor
```

## Configuration

- Image sizes available: 1024x1024 (square), 1024x1792 (portrait), 1792x1024 (landscape)
- Quality options: standard (default), hd (enhanced detail)
- Generated images are saved in the `images` directory with timestamps

## License

MIT License 