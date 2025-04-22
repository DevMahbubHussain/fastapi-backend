FROM python:3.11-slim

WORKDIR /app

# Copy only the requirements.txt to leverage Docker caching
COPY requirements.txt .

# Install dependencies (upgrade pip once and install requirements)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . . 


# Expose the port FastAPI is running on
EXPOSE 8000

# Command to run the application
CMD ["/app/wait-for-it.sh", "db:5432", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

