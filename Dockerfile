FROM python:3.12-slim-bullseye

# Set the working directory.
WORKDIR /app

# Copy requirements and install dependencies.
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy only the api and app directories.
COPY api/ api/
COPY app/ app/

# Expose port 8000 for the API.
EXPOSE 8000

# Run the FastAPI app with uvicorn.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]