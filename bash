#!/bin/bash

set -e  # Exit on any error
LOG_FILE="/var/log/launch-script.log"

exec > >(tee -a "$LOG_FILE") 2>&1
echo "=== Launch script started at $(date) ==="

# Step 1: Update and install system packages
echo "Installing Git, Nginx, Python3..."
sudo yum update -y
sudo yum install -y git nginx python3-pip

# Step 2: Clone or update the repository
cd /home/ec2-user
if [ -d "scrapes_flask" ]; then
  echo "Repository exists. Pulling latest changes..."
  cd scrapes_flask
  git pull
else
  echo "Cloning repository..."
  git clone https://github.com/cocrsmccue/scrapes_flask.git
  cd scrapes_flask
fi

# Step 3: Install Python requirements
if [ -f "requirements.txt" ]; then
  echo "Installing Python dependencies..."
  pip3 install --user -r requirements.txt
else
  echo "requirements.txt not found! Aborting."
  exit 1
fi

# Step 4: Configure Nginx and systemd service
echo "Copying config files..."
sudo cp config/nginx.conf /etc/nginx/nginx.conf
sudo cp config/scrapes_flask.service /etc/systemd/system/scrapes_flask.service

# Step 5: Start and enable services
echo "Starting Nginx..."
sudo systemctl enable nginx
sudo systemctl restart nginx

echo "Starting scrapes_flask (Gunicorn)..."
sudo systemctl daemon-reload
sudo systemctl enable scrapes_flask
sudo systemctl restart scrapes_flask

echo "=== Launch script completed successfully at $(date) ==="
