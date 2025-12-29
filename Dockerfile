# Stage 1 Phase 3: Production-ready Docker image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages with C extensions
# Build dependencies (will be removed after pip install):
#   - build-essential: gcc, g++, make for compiling
#   - pkg-config: helps find installed libraries
#   - libcairo2-dev: Cairo graphics library development files (required by pycairo)
# Runtime dependencies (will be kept):
#   - libcairo2: Cairo graphics library (required by pycairo at runtime)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        libcairo2-dev \
        libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Remove build dependencies to reduce image size, keeping only runtime libraries
RUN apt-get purge -y --auto-remove \
        build-essential \
        pkg-config \
        libcairo2-dev

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
