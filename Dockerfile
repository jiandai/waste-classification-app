# Stage 1 Phase 3: Production-ready Docker image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend application files
COPY backend/app /app/backend/app

# Copy web frontend files
COPY web /app/web

# Create a non-root user to run the application
# Using UID 1000 which is a common default; override with docker build --build-arg if needed
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
