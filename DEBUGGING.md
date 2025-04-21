# Debugging the Marvin Art Generator Container

This guide provides instructions for debugging issues with the Marvin Art Generator container.

## Debugging Tools

We've created two files to help with debugging:

1. `docker-compose.debug.yml` - A modified Docker Compose file that runs the container with a shell instead of the Python script (using the new project structure)
2. `debug_container.sh` - A shell script that runs diagnostic tests on the container

## How to Use the Debugging Tools

### On Your Server

1. Pull the latest changes from the repository:

```bash
cd /opt/marvin
git pull
```

2. Make the debug script executable:

```bash
chmod +x debug_container.sh
```

3. Run the debug script:

```bash
./debug_container.sh
```

The script will:
- Stop any running containers
- Start the container with the debug configuration
- Check environment variables
- Test database connectivity
- Verify the OpenAI API key
- Provide instructions for manual debugging

### Manual Debugging

If the script doesn't identify the issue, you can connect to the container and run the script manually:

```bash
# Get the container ID
CONTAINER_ID=$(docker ps -q --filter "name=marvin_marvin-art")

# Connect to the container
docker exec -it $CONTAINER_ID /bin/bash

# Inside the container, run:
python marvin_art.py
```

This will show the full error message if the script crashes.

## Common Issues and Solutions

### 1. Database Connection Issues

If the container can't connect to the Supabase database:
- Verify that the SUPABASE_URL and SUPABASE_KEY environment variables are set correctly
- Check if the database tables exist (characters, prompts, images, feedback)
- Ensure your IP address is allowed in the Supabase dashboard

### 2. OpenAI API Issues

If the container can't connect to the OpenAI API:
- Verify that the OPENAI_API_KEY environment variable is set correctly
- Check if the API key has sufficient credits
- Ensure the API key has the necessary permissions

### 3. Port Conflicts

If another service is using port 8000:
- Change the port mapping in the docker-compose.yml file
- Stop the conflicting service

### 4. Resource Constraints

If the container is running out of resources:
- Check the container's resource usage with `docker stats`
- Increase the memory limit in the docker-compose.yml file

## Cleanup

When you're done debugging, stop the debug container:

```bash
docker-compose -f docker-compose.debug.yml down
```

Then restart the regular container:

```bash
docker-compose up -d
```
