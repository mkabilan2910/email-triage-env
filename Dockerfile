# Dockerfile — packages our environment for deployment

# Start with a lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy all our project files into the container
COPY . .

# Install all required packages
RUN pip install --no-cache-dir \
    openenv-core \
    fastapi \
    uvicorn \
    pydantic \
    openai \
    huggingface_hub \
    requests

# Expose port 8000 so the outside world can talk to our server
EXPOSE 8000

# Command to start the server when container runs
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]