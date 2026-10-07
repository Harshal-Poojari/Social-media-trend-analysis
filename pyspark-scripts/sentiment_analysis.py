#!/usr/bin/env python3

"""
Sentiment Analysis for Social Media Posts using PySpark
This script performs sentiment analysis on social media posts
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType, IntegerType
from textblob import TextBlob
import sys

def get_sentiment(text):
    """
    Analyze sentiment of text using TextBlob
    Returns: 'positive', 'negative', or 'neutral'
    """
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    except:
        return 'neutral'

def get_sentiment_score(text):
    """
    Get sentiment score (-1 to 1)
    """
    try:
        analysis = TextBlob(text)
        return analysis.sentiment.polarity
    except:
        return 0.0

def main():
    # Initialize Spark Session with Hive support
    spark = SparkSession.builder \
        .appName("SocialMediaSentimentAnalysis") \
        .enableHiveSupport() \
        .getOrCreate()
    
    print("Spark Session created successfully")
    print("=" * 50)
    
    # Load data from Hive table
    print("Loading data from Hive table social_media.posts...")
    df = spark.sql("SELECT * FROM social_media.posts")
    
    print(f"Total records loaded: {df.count()}")
    
    # Register UDFs
    sentiment_udf = udf(get_sentiment, StringType())
    sentiment_score_udf = udf(get_sentiment_score, IntegerType())
    
    # Apply sentiment analysis
    print("\nPerforming sentiment analysis...")
    df_with_sentiment = df.withColumn("sentiment", sentiment_udf(col("text")))
    df_with_sentiment = df_with_sentiment.withColumn("sentiment_score", sentiment_score_udf(col("text")))
    
    # Show sample results
    print("\nSample sentiment analysis results:")
    df_with_sentiment.select("id", "text", "sentiment", "sentiment_score").show(10, truncate=False)
    
    # Sentiment distribution
    print("\n" + "=" * 50)
    print("SENTIMENT DISTRIBUTION")
    print("=" * 50)
    
    sentiment_dist = df_with_sentiment.groupBy("sentiment") \
        .agg(
            count("*").alias("count"),
            avg("likes").alias("avg_likes"),
            avg("shares").alias("avg_shares"),
            avg("comments").alias("avg_comments")
        ) \
        .orderBy(col("count").desc())
    
    sentiment_dist.show()
    
    # Sentiment by platform
    print("\n" + "=" * 50)
    print("SENTIMENT BY PLATFORM")
    print("=" * 50)
    
    sentiment_platform = df_with_sentiment.groupBy("platform", "sentiment") \
        .agg(count("*").alias("count")) \
        .orderBy("platform", "sentiment")
    
    sentiment_platform.show()
    
    # Sentiment by hashtag
    print("\n" + "=" * 50)
    print("SENTIMENT BY HASHTAG")
    print("=" * 50)
    
    from pyspark.sql.functions import split, explode
    
    df_with_hashtags = df_with_sentiment.withColumn("hashtag_array", split(col("hashtags"), " "))
    df_exploded = df_with_hashtags.select("*", explode(col("hashtag_array")).alias("hashtag"))
    df_hashtags = df_exploded.filter(col("hashtag") != "")
    
    sentiment_hashtag = df_hashtags.groupBy("hashtag", "sentiment") \
        .agg(count("*").alias("count")) \
        .orderBy("hashtag", "sentiment")
    
    sentiment_hashtag.show(20, truncate=False)
    
    # Average engagement by sentiment
    print("\n" + "=" * 50)
    print("AVERAGE ENGAGEMENT BY SENTIMENT")
    print("=" * 50)
    
    engagement_sentiment = df_with_sentiment.groupBy("sentiment") \
        .agg(
            avg("likes").alias("avg_likes"),
            avg("shares").alias("avg_shares"),
            avg("comments").alias("avg_comments")
        ) \
        .withColumn("avg_engagement", 
                   col("avg_likes") + col("avg_shares") + col("avg_comments"))
    
    engagement_sentiment.show()
    
    # Save results to CSV
    print("\n" + "=" * 50)
    print("Saving sentiment analysis results...")
    print("=" * 50)
    
    sentiment_dist.write.mode("overwrite").csv("output/sentiment_distribution.csv", header=True)
    sentiment_platform.write.mode("overwrite").csv("output/sentiment_by_platform.csv", header=True)
    engagement_sentiment.write.mode("overwrite").csv("output/sentiment_engagement.csv", header=True)
    
    # Save full dataset with sentiment
    df_with_sentiment.select("id", "date", "platform", "user", "text", "hashtags", 
                            "likes", "shares", "comments", "sentiment", "sentiment_score") \
        .write.mode("overwrite") \
        .csv("output/posts_with_sentiment.csv", header=True)
    
    print("Sentiment analysis results saved to output/ directory")
    
    # Stop Spark Session
    spark.stop()
    print("\nSentiment analysis completed successfully!")

if __name__ == "__main__":
    main()
