# Use the official Python image as a base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

RUN echo "Building the Docker image"

# Install any dependencies
RUN apt-get update && \
    apt-get install -y firefox-esr && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install geckodriver (Firefox driver)
RUN echo "Installing geckodriver (Firefox driver)"
RUN apt-get update && \
    apt-get install -y wget && \
    wget -O geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz && \
    tar -xzf geckodriver.tar.gz && \
    mv geckodriver /usr/local/bin/ && \
    rm geckodriver.tar.gz && \
    apt-get remove -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN echo "Installing Python dependencies"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 10000

# Define the command to run your application
CMD ["python", "gyts.py"]
