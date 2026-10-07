#!/bin/bash

# HDFS Setup Script for Social Media Trend Analysis Project
# This script sets up HDFS directories and loads the dataset

echo "Starting HDFS setup for Social Media Trend Analysis..."

# Start HDFS if not already running
echo "Checking HDFS status..."
start-dfs.sh

# Wait for HDFS to start
sleep 10

# Create HDFS directory for social media data
echo "Creating HDFS directory /socialmedia..."
hdfs dfs -mkdir -p /socialmedia

# Check if directory was created
echo "Verifying HDFS directory creation..."
hdfs dfs -ls /

# Upload dataset to HDFS
echo "Uploading social_media.csv to HDFS..."
hdfs dfs -put dataset/social_media.csv /socialmedia/

# Verify file upload
echo "Verifying file upload..."
hdfs dfs -ls /socialmedia/

# Display file content (first 5 lines)
echo "Displaying first 5 lines of uploaded data..."
hdfs dfs -cat /socialmedia/social_media.csv | head -5

echo "HDFS setup completed successfully!"
echo "Dataset location: /socialmedia/social_media.csv"
