# Dockerfile

# 1. Start from Python base image
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy your app files into the container
COPY . .

# 4. Install required Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Expose port (Flask default)
EXPOSE 5000

# 6. Run your app
CMD ["python", "app.py"]
