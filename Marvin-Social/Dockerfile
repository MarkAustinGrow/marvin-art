FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Install specific version of gotrue before other dependencies
RUN pip install --no-cache-dir gotrue==2.8.0

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make sure the social_agent.py file is in the correct location
RUN ls -la

CMD ["uvicorn", "social_agent:app", "--host", "0.0.0.0", "--port", "8001"]
