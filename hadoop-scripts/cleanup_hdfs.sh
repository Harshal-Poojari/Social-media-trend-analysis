#!/bin/bash

# HDFS Cleanup Script
# This script removes the social media data from HDFS

echo "Cleaning up HDFS social media data..."

# Remove the social media directory
hdfs dfs -rm -r /socialmedia

echo "HDFS cleanup completed!"
