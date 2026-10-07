-- Hive Table Creation Script for Social Media Trend Analysis
-- Run this in Hive CLI: hive -f create_table.hql

-- Create database
CREATE DATABASE IF NOT EXISTS social_media;
USE social_media;

-- Drop table if exists
DROP TABLE IF EXISTS posts;

-- Create external table for social media posts
CREATE EXTERNAL TABLE posts (
    id INT,
    date STRING,
    platform STRING,
    user STRING,
    text STRING,
    hashtags STRING,
    likes INT,
    shares INT,
    comments INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/socialmedia';

-- Load data from HDFS
LOAD DATA INPATH '/socialmedia/social_media.csv' OVERWRITE INTO TABLE posts;

-- Verify data loaded
SELECT COUNT(*) AS total_posts FROM posts;

-- Display sample data
SELECT * FROM posts LIMIT 5;
