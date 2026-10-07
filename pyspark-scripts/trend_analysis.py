#!/usr/bin/env python3

"""
Social Media Trend Analysis using PySpark
This script processes social media data from Hive and performs trend analysis
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, sum, when, lit, explode, split
from pyspark.sql.types import IntegerType, StringType
import sys

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("SocialMediaTrendAnalysis") \
        .getOrCreate()
    
    print("Spark Session created successfully")
    print("=" * 50)
    
    # Load data from CSV file
    print("Loading data from CSV file...")
    df = spark.read.csv("../dataset/social_media.csv", header=True, inferSchema=True)
    
    print(f"Total records loaded: {df.count()}")
    print("\nSample data:")
    df.show(5, truncate=False)
    
    # Analysis 1: Hashtag Trend Analysis
    print("\n" + "=" * 50)
    print("ANALYSIS 1: Hashtag Trend Analysis")
    print("=" * 50)
    
    # Split hashtags and explode
    df_with_hashtags = df.withColumn("hashtag_array", split(col("hashtags"), " "))
    df_exploded = df_with_hashtags.select("*", explode(col("hashtag_array")).alias("hashtag"))
    
    # Filter out empty strings and non-hashtag entries
    df_hashtags = df_exploded.filter(col("hashtag") != "")
    
    # Calculate hashtag statistics
    hashtag_stats = df_hashtags.groupBy("hashtag") \
        .agg(
            count("*").alias("post_count"),
            avg("likes").alias("avg_likes"),
            avg("shares").alias("avg_shares"),
            avg("comments").alias("avg_comments"),
            sum("likes").alias("total_likes"),
            sum("shares").alias("total_shares"),
            sum("comments").alias("total_comments")
        ) \
        .withColumn("total_engagement", col("total_likes") + col("total_shares") + col("total_comments")) \
        .withColumn("avg_engagement", col("avg_likes") + col("avg_shares") + col("avg_comments")) \
        .orderBy(col("post_count").desc())
    
    print("\nTop Hashtags by Post Count:")
    hashtag_stats.show(10, truncate=False)
    
    # Calculate Trend Score
    # Trend Score = Frequency (0.4) + Engagement (0.4) + Growth (0.2)
    # For simplicity, we'll use normalized values
    max_posts = hashtag_stats.agg({"post_count": "max"}).collect()[0][0]
    max_engagement = hashtag_stats.agg({"total_engagement": "max"}).collect()[0][0]
    
    hashtag_stats = hashtag_stats.withColumn("normalized_frequency", col("post_count") / lit(max_posts)) \
        .withColumn("normalized_engagement", col("total_engagement") / lit(max_engagement)) \
        .withColumn("trend_score", 
                    (col("normalized_frequency") * 0.4) + 
                    (col("normalized_engagement") * 0.4) + 
                    (lit(0.2)))  # Default growth factor
    
    print("\nHashtags by Trend Score:")
    hashtag_stats.select("hashtag", "post_count", "total_engagement", "trend_score") \
        .orderBy(col("trend_score").desc()) \
        .show(10, truncate=False)
    
    # Analysis 2: Platform Analysis
    print("\n" + "=" * 50)
    print("ANALYSIS 2: Platform Analysis")
    print("=" * 50)
    
    platform_stats = df.groupBy("platform") \
        .agg(
            count("*").alias("post_count"),
            avg("likes").alias("avg_likes"),
            avg("shares").alias("avg_shares"),
            avg("comments").alias("avg_comments"),
            sum("likes").alias("total_likes"),
            sum("shares").alias("total_shares"),
            sum("comments").alias("total_comments")
        ) \
        .withColumn("total_engagement", col("total_likes") + col("total_shares") + col("total_comments")) \
        .withColumn("avg_engagement", col("avg_likes") + col("avg_shares") + col("avg_comments")) \
        .orderBy(col("total_engagement").desc())
    
    print("\nPlatform Statistics:")
    platform_stats.show(truncate=False)
    
    # Analysis 3: Top Performing Posts
    print("\n" + "=" * 50)
    print("ANALYSIS 3: Top Performing Posts")
    print("=" * 50)
    
    df_with_engagement = df.withColumn("engagement", col("likes") + col("shares") + col("comments"))
    
    top_posts = df_with_engagement.select(
        "id", "date", "platform", "user", "text", "hashtags", 
        "likes", "shares", "comments", "engagement"
    ).orderBy(col("engagement").desc())
    
    print("\nTop 10 Posts by Engagement:")
    top_posts.show(10, truncate=False)
    
    # Analysis 4: Daily Trend Analysis
    print("\n" + "=" * 50)
    print("ANALYSIS 4: Daily Trend Analysis")
    print("=" * 50)
    
    daily_stats = df.groupBy("date") \
        .agg(
            count("*").alias("post_count"),
            sum("likes").alias("total_likes"),
            sum("shares").alias("total_shares"),
            sum("comments").alias("total_comments")
        ) \
        .withColumn("total_engagement", col("total_likes") + col("total_shares") + col("total_comments")) \
        .orderBy("date")
    
    print("\nDaily Statistics:")
    daily_stats.show(truncate=False)
    
    # Analysis 5: User Engagement Analysis
    print("\n" + "=" * 50)
    print("ANALYSIS 5: User Engagement Analysis")
    print("=" * 50)
    
    user_stats = df.groupBy("user") \
        .agg(
            count("*").alias("post_count"),
            avg("likes").alias("avg_likes"),
            avg("shares").alias("avg_shares"),
            avg("comments").alias("avg_comments"),
            sum("likes").alias("total_likes"),
            sum("shares").alias("total_shares"),
            sum("comments").alias("total_comments")
        ) \
        .withColumn("total_engagement", col("total_likes") + col("total_shares") + col("total_comments")) \
        .orderBy(col("total_engagement").desc())
    
    print("\nTop 10 Users by Engagement:")
    user_stats.show(10, truncate=False)
    
    # Save results to CSV for R visualization
    print("\n" + "=" * 50)
    print("Saving results to CSV files...")
    print("=" * 50)
    
    hashtag_stats.select("hashtag", "post_count", "avg_likes", "avg_shares", "avg_comments", 
                        "total_engagement", "trend_score") \
        .write.mode("overwrite") \
        .csv("output/hashtag_analysis.csv", header=True)
    
    platform_stats.select("platform", "post_count", "avg_likes", "avg_shares", "avg_comments", 
                         "total_engagement") \
        .write.mode("overwrite") \
        .csv("output/platform_analysis.csv", header=True)
    
    daily_stats.select("date", "post_count", "total_likes", "total_shares", "total_comments", 
                      "total_engagement") \
        .write.mode("overwrite") \
        .csv("output/daily_trends.csv", header=True)
    
    top_posts.select("id", "date", "platform", "user", "hashtags", "likes", "shares", 
                    "comments", "engagement") \
        .write.mode("overwrite") \
        .csv("output/top_posts.csv", header=True)
    
    user_stats.select("user", "post_count", "avg_likes", "avg_shares", "avg_comments", 
                     "total_engagement") \
        .write.mode("overwrite") \
        .csv("output/user_analysis.csv", header=True)
    
    print("Results saved to output/ directory")
    
    # Stop Spark Session
    spark.stop()
    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()
