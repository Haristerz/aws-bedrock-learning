#!/bin/bash
# EC2 Setup Script
# Run this after launching EC2 instance
# Author: Hari
# Date: 2026

echo "Starting EC2 setup..."

# Step 1 - Update system
echo "Updating system..."
sudo yum update -y

# Step 2 - Install Docker
echo "Installing Docker..."
sudo yum install docker -y

# Step 3 - Start Docker
echo "Starting Docker..."
sudo service docker start

# Step 4 - Add user to Docker group
echo "Adding user to Docker group..."
sudo usermod -a -G docker ec2-user

# Step 5 - Install AWS CLI
echo "Installing AWS CLI..."
sudo yum install awscli -y

# Step 6 - Verify installations
echo "Verifying installations..."
docker --version
aws --version

echo "Setup complete! Log out and log back in."
