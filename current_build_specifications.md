# Marvin Art Generator - Current Build Specifications

## Overview

Marvin Art Generator is an AI-powered system that creates unique digital artwork using advanced AI models. The system generates creative prompts based on Marvin's artistic character, transforms these prompts into visual art using DALL-E 3, and provides a user-friendly web interface for viewing and generating new artwork.

## Key Features

### Art Generation
- **AI-Powered Creativity**: Uses GPT-4 to generate unique, creative art prompts
- **High-Quality Images**: Creates detailed artwork using DALL-E 3
- **Character-Based**: Art reflects Marvin's unique artistic style and preferences
- **Two Generation Modes**:
  - Automatic generation (scheduled, 2 per day)
  - Manual generation (on-demand, unlimited)

### Web Interface
- **Responsive Gallery**: View all generated artwork in a modern, responsive grid
- **Detailed Information**: See full prompts and generation details for each image
- **One-Click Generation**: Create new artwork with a single button press
- **Image Details Modal**: Examine artwork in detail with full metadata

### Image Storage System
- **Permanent Storage**: All images stored in Supabase Storage for long-term access
- **Multi-Layered Fallback**: Four-tier approach ensures images always display:
  1. Supabase Storage (primary)
  2. Local file storage (backup)
  3. Original DALL-E URLs (temporary)
  4. Placeholder image (last resort)
- **Organization**: Images stored in timestamped folders for easy management


### System Features
- **Comprehensive Logging**: Detailed event and error tracking
- **Database Storage**: All data stored in Supabase for reliability
- **API Access**: Full API for programmatic access to all features
- **Containerized Deployment**: Easy deployment with Docker

## Technical Specifications

### Core Technologies
- **Backend**: Python with FastAPI
- **AI Models**: OpenAI GPT-4 and DALL-E 3
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage
- **Containerization**: Docker

### System Architecture
- **Marvin Art Generator**: Core service for art generation and API (Port 8000)
- **Web Interface**: Frontend for user interaction
- **Logging System**: Comprehensive event and error tracking

### Database Schema
- **character_files**: Character definitions and personalities
- **prompts**: Generated art prompts
- **images**: Generated images with metadata
- **marvin_art_logs**: Application logs and events

### API Endpoints
- `GET /`: Web interface
- `POST /generate`: Generate new art
- `GET /images`: Retrieve generated images
- `GET /proxy-image/{image_id}`: Serve images with fallback
- `POST /trigger-generation`: Manually trigger generation
- `GET /logs`: Access system logs

## Deployment Information

### Requirements
- Docker and Docker Compose
- Internet connectivity for OpenAI and Supabase
- Environment variables:
  - `OPENAI_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_KEY`

### Deployment Process
- Pull from GitHub repository
- Configure environment variables
- Run with Docker Compose
- Access web interface at port 8000

## Recent Enhancements

### Supabase Storage Integration
- **Permanent Image Storage**: Images now stored in Supabase Storage for long-term access
- **URL Stability**: Eliminates issues with expiring DALL-E URLs
- **Improved Reliability**: Multi-layered fallback system ensures images always display

### Enhanced Proxy System
- **Smart Image Serving**: Automatically selects the best available image source
- **Graceful Degradation**: Falls back to alternative sources if primary is unavailable
- **Placeholder Support**: Ensures UI integrity even when images can't be found

### Comprehensive Logging
- **Database Logging**: All system events stored in Supabase
- **Structured Metadata**: Rich context for debugging and analysis
- **Log Management**: Automatic cleanup of old logs
