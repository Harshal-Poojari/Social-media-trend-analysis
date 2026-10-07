-- Hive Analysis Queries for Social Media Trend Analysis
-- Run individual queries in Hive CLI

USE social_media;

-- Query 1: Find most popular hashtags
SELECT 
    hashtags,
    COUNT(*) AS post_count,
    SUM(likes) AS total_likes,
    SUM(shares) AS total_shares,
    SUM(comments) AS total_comments,
    SUM(likes + shares + comments) AS total_engagement
FROM posts
GROUP BY hashtags
ORDER BY post_count DESC;

-- Query 2: Find highest engagement posts
SELECT 
    id,
    date,
    platform,
    user,
    hashtags,
    likes,
    shares,
    comments,
    (likes + shares + comments) AS engagement
FROM posts
ORDER BY engagement DESC
LIMIT 10;

-- Query 3: Average engagement by platform
SELECT 
    platform,
    COUNT(*) AS post_count,
    AVG(likes) AS avg_likes,
    AVG(shares) AS avg_shares,
    AVG(comments) AS avg_comments,
    AVG(likes + shares + comments) AS avg_engagement
FROM posts
GROUP BY platform
ORDER BY avg_engagement DESC;

-- Query 4: Daily activity analysis
SELECT 
    date,
    COUNT(*) AS posts_per_day,
    SUM(likes) AS total_likes,
    SUM(shares) AS total_shares,
    SUM(comments) AS total_comments
FROM posts
GROUP BY date
ORDER BY date;

-- Query 5: Top users by engagement
SELECT 
    user,
    COUNT(*) AS post_count,
    SUM(likes) AS total_likes,
    SUM(shares) AS total_shares,
    SUM(comments) AS total_comments,
    SUM(likes + shares + comments) AS total_engagement
FROM posts
GROUP BY user
ORDER BY total_engagement DESC
LIMIT 10;

-- Query 6: Hashtag engagement analysis
SELECT 
    hashtags,
    AVG(likes) AS avg_likes,
    AVG(shares) AS avg_shares,
    AVG(comments) AS avg_comments,
    AVG(likes + shares + comments) AS avg_engagement
FROM posts
GROUP BY hashtags
ORDER BY avg_engagement DESC;
