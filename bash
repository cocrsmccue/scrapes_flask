#!/bin/bash

# Fail on any error
set -e

# Optional: Log the start
echo "Starting EC2 launch script at $(date)"

# Step 1: Install necessary packages
sudo yum update -y
sudo yum install -y git nginx python3-pip

# Step 2: Clone the GitHub repository (skip if it already exists)
cd /home/ec2-user
if [ ! -d "scrapes_flask" ]; then
  git clone https://github.com/cocrsmccue/scrapes_flask.git
fi

# Step 3: Install Python dependencies
cd scrapes_flask
pip3 install --user -r requirements.txt

# Step 4: Copy Nginx and Gunicorn config files
sudo cp config/nginx.conf /etc/nginx/nginx.conf
sudo cp config/scrapes_flask.service /etc/systemd/system/scrapes_flask.service

# Step 5: Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx

# Step 6: Enable and start your Gunicorn Flask app
sudo systemctl daemon-reload
sudo systemctl enable scrapes_flask
sudo systemctl restart scrapes_flask

echo "Launch script complete at $(date)"

