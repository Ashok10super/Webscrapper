# 1. Use the official Python 3.10 image (from your logs)
FROM python:3.10-slim

# 2. Set the working directory inside the container
# This matches the path in your error logs
WORKDIR /webscrapper

# 3. Copy *only* the requirements file first
COPY requirements.txt .

# 4. Install dependencies
# This is done in its own step for better Docker layer caching
RUN pip install -r requirements.txt

# 5. Copy ALL other files from your project (main.py, bot.py, etc.)
# This is the line that fixes your error.
COPY . .

# 6. Define the command to run your app
# This uses the port 8080 from your logs and assumes your
# FastAPI/Flask app object in main.py is named 'app'
CMD ["gunicorn", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:8080", "eauctionsindia.main:app"]