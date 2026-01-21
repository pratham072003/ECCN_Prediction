# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8000 for the API
EXPOSE 8000

# Define environment variable (Can be overridden at runtime)
#ENV OPENAI_API_KEY=your_key_here

# Run main.py when the container launches
CMD ["python", "main.py"]
