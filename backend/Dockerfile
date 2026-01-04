# 1. Use an official Python runtime as a parent image
FROM python:3.10-slim

# 2. Install system dependencies (Tesseract + OpenCV requirements)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
WORKDIR /app

# 4. Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Download spaCy language model (required for NER)
RUN python -m spacy download en_core_web_sm

# 6. Copy the rest of the application code
COPY . .

# 7. Expose the port the app runs on (Render uses 10000 by default)
EXPOSE 8000

# 8. Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]