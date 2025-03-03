FROM python:3.9-slim

# Install necessary system dependencies for downloading and extracting Chrome
RUN apt-get update && \
    apt-get install -y wget dpkg apt-transport-https gnupg2 && \
    rm -rf /var/lib/apt/lists/*

# Download and extract Google Chrome if not already cached
RUN set -o errexit; \
    STORAGE_DIR=/opt/render/project/.render; \
    mkdir -p $STORAGE_DIR/chrome; \
    wget -q -P $STORAGE_DIR/chrome https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb; \
    dpkg -x $STORAGE_DIR/chrome/google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome; \
    rm $STORAGE_DIR/chrome/google-chrome-stable_current_amd64.deb

# Add Chrome's location to the PATH so Selenium can find it
ENV PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome"

# Install chromedriver via apt-get
RUN apt-get update && \
    apt-get install -y chromedriver && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables for Selenium to use
ENV CHROME_BIN=/opt/render/project/.render/chrome/opt/google/chrome/google-chrome
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your app runs on
EXPOSE 10000

# Command to run your FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
