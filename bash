#!/bin/bash

set -e  # Exit on any error
LOG_FILE="/var/log/launch-script.log"

exec > >(tee -a "$LOG_FILE") 2>&1
echo "=== Launch script started at $(date) ==="

# Step 1: Update and install system packages
echo "Installing Git, Nginx, Python3, unzip..."
sudo yum update -y
sudo yum install -y git nginx python3-pip unzip

# Step 2: Install AWS CLI v2
echo "Installing AWS CLI v2..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip
aws --version

# Step 3: Clone or update repo as ec2-user (to preserve permissions)
sudo -u ec2-user bash << 'EOF'
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
EOF

# Step 4: Install Python requirements system-wide
cd /home/ec2-user/scrapes_flask

# Optional: remove problematic packages if not already removed
sed -i '/awscli==2/d' requirements.txt || true
sed -i '/gpg==1.15.1/d' requirements.txt || true

if [ -f "requirements.txt" ]; then
  echo "Installing Python dependencies system-wide..."
  sudo pip3 install -r requirements.txt
else
  echo "requirements.txt not found! Aborting."
  exit 1
fi

# Step 5: Copy Nginx and systemd service files
echo "Copying config files..."
sudo cp config/nginx.conf /etc/nginx/nginx.conf
sudo cp config/scrapes_flask.service /etc/systemd/system/scrapes_flask.service

# Step 6: Enable and start services
echo "Starting Nginx..."
sudo systemctl enable nginx
sudo systemctl restart nginx

echo "Starting scrapes_flask (Gunicorn)..."
sudo systemctl daemon-reload
sudo systemctl enable scrapes_flask
sudo systemctl restart scrapes_flask

echo "=== Launch script completed successfully at $(date) ==="
