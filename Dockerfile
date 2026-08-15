FROM python:3.11-slim

WORKDIR /app

# Copy project
COPY . /app

# Install system deps
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=8501", "--server.headless=true"]
