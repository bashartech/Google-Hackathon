# Use an official lightweight Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860 \
    HOME=/home/user

# Install system dependencies if any are needed (none for psycopg2-binary, but curl is good for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user with UID 1000 to match Hugging Face Space security requirements
RUN useradd -m -u 1000 user

# Set working directory inside the user's home
WORKDIR $HOME/app

# Copy the requirements file first to take advantage of Docker layer caching
COPY --chown=user:user requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=user:user . .

# Ensure the log file is writable by the non-root user
RUN touch backend.log && chown user:user backend.log && chmod 666 backend.log

# Switch to the non-root user
USER user

# Expose Hugging Face Space standard port
EXPOSE 7860

# Run uvicorn on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
