# 1. Start from a standard Python image
FROM python:3.10-slim

# 2. Switch to root user to install system packages
USER root

# 3. Install tesseract-ocr
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory in the container
WORKDIR /

# 5. Copy and install Python requirements
# (This assumes requirements.txt is in your root. If not, tell me)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy all your code into the container
# (This will copy the 'webscrapper' folder into /)
COPY . .

# 7. Set the command to run the web server
# --- THIS IS THE CORRECTED LINE ---
# The path starts with 'webscrapper' because your WORKDIR is /
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 eauctionsindiabot.main:app
