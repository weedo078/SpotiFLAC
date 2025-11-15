# SpotiFLAC Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # For PyQt6
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    # For Chrome/Selenium
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for headless operation
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=offscreen
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /downloads

# Set volume for downloads
VOLUME ["/downloads"]

# Expose port for potential web interface (future feature)
EXPOSE 8080

# Set default output directory
ENV SPOTIFLAC_OUTPUT_DIR=/downloads

# Run the application
CMD ["python", "-m", "spotiflac.app"]
