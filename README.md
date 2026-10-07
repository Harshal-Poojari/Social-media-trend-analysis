# Social Media Trend Analysis Using Hadoop, Hive, PySpark and R

A comprehensive Big Data project that analyzes social media trends from multiple platforms (Twitter, Instagram, etc.) using Hadoop ecosystem tools and R for visualization.

## Project Architecture

```
Social Media Data
        ↓
    Hadoop/HDFS
        ↓
    Apache Hive
        ↓
Data Cleaning & Aggregation
        ↓
    PySpark
        ↓
Trend Detection & Sentiment Analysis
        ↓
    R
Visualization & Analysis
```

## Features

This project analyzes:
1. **Trending Hashtags** - Most used and rapidly growing hashtags
2. **Engagement Analysis** - Likes, shares, comments, and engagement rates
3. **Time-based Trends** - Most active days, hours, and trend growth over time
4. **Sentiment Analysis** - Positive, negative, and neutral sentiment classification
5. **Top-performing Posts** - Posts with highest engagement
6. **Platform Comparison** - Analysis across Twitter, Instagram, and other platforms
7. **Trend Visualization** - Interactive dashboards and charts

## Project Structure

```
Social_Media_Trend_Analysis/
├── dataset/
│   └── social_media.csv          # Sample social media dataset
├── hadoop-scripts/
│   ├── setup_hdfs.sh            # HDFS setup script
│   └── cleanup_hdfs.sh          # HDFS cleanup script
├── hive-scripts/
│   ├── create_table.hql         # Hive table creation script
│   └── analysis_queries.hql     # Hive analysis queries
├── pyspark-scripts/
│   ├── trend_analysis.py        # PySpark trend analysis
│   └── sentiment_analysis.py    # PySpark sentiment analysis
├── r-scripts/
│   ├── visualizations.R         # R visualization script
│   └── install_packages.R       # R package installation
├── output/                      # Output directory for analysis results
└── README.md                    # This file
```

## Prerequisites

- Ubuntu (preferably via WSL2 on Windows)
- Java 8 or higher
- Hadoop (single-node setup)
- Apache Hive
- Python 3.x
- PySpark
- R / RStudio
- TextBlob (for sentiment analysis)

## Installation Guide

See `UBUNTU_SETUP.md` for detailed installation instructions.

To run or deploy the Flask dashboard, see [`web-app/DEPLOYMENT.md`](web-app/DEPLOYMENT.md).

## Quick Start

### 1. Setup HDFS

```bash
cd hadoop-scripts
chmod +x setup_hdfs.sh
./setup_hdfs.sh
```

### 2. Create Hive Table

```bash
cd hive-scripts
hive -f create_table.hql
```

### 3. Run Hive Analysis Queries

```bash
hive -f analysis_queries.hql
```

Or run individual queries in Hive CLI:

```bash
hive
USE social_media;
SELECT hashtag, COUNT(*) AS count FROM posts GROUP BY hashtag ORDER BY count DESC;
```

### 4. Run PySpark Analysis

```bash
cd pyspark-scripts

# Trend Analysis
spark-submit trend_analysis.py

# Sentiment Analysis (requires TextBlob)
pip install textblob
spark-submit sentiment_analysis.py
```

### 5. Create Visualizations in R

```bash
cd r-scripts

# Install required packages
Rscript install_packages.R

# Run visualizations
Rscript visualizations.R
```

## Dataset Format

The dataset should be in CSV format with the following columns:

| Column | Description |
|--------|-------------|
| id | Unique post identifier |
| date | Post date (YYYY-MM-DD) |
| platform | Platform name (Twitter, Instagram, etc.) |
| user | Username |
| text | Post content |
| hashtags | Comma-separated hashtags |
| likes | Number of likes |
| shares | Number of shares |
| comments | Number of comments |

## Analysis Outputs

The project generates the following outputs:

### PySpark Outputs (in `output/` directory)
- `hashtag_analysis.csv` - Hashtag statistics and trend scores
- `platform_analysis.csv` - Platform engagement metrics
- `daily_trends.csv` - Daily activity trends
- `top_posts.csv` - Top performing posts
- `user_analysis.csv` - User engagement statistics
- `sentiment_distribution.csv` - Sentiment analysis results
- `sentiment_by_platform.csv` - Sentiment by platform
- `sentiment_engagement.csv` - Engagement by sentiment

### R Visualizations (in `output/plots/` directory)
- `top_hashtags.png` - Top 10 trending hashtags
- `trend_score.png` - Hashtags by trend score
- `platform_engagement.png` - Total engagement by platform
- `avg_platform_engagement.png` - Average engagement by platform
- `daily_volume.png` - Daily post volume
- `daily_engagement.png` - Daily engagement trends
- `sentiment_distribution.png` - Sentiment distribution
- `engagement_by_sentiment.png` - Engagement by sentiment
- `hashtag_engagement.png` - Hashtags by engagement
- `dashboard.png` - Combined dashboard view

## Key Features Explained

### Trend Score Calculation

The trend score is calculated using the formula:

```
Trend Score = (Frequency × 0.4) + (Engagement × 0.4) + (Growth Rate × 0.2)
```

Where:
- **Frequency**: Normalized post count for the hashtag
- **Engagement**: Normalized total engagement (likes + shares + comments)
- **Growth Rate**: Default factor (can be enhanced with time-series data)

### Sentiment Analysis

Uses TextBlob to analyze post sentiment:
- **Positive**: Polarity > 0.1
- **Negative**: Polarity < -0.1
- **Neutral**: -0.1 ≤ Polarity ≤ 0.1

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Ubuntu | Operating environment |
| Hadoop/HDFS | Distributed storage |
| Apache Hive | SQL-based data warehousing |
| PySpark | Big data processing |
| Python | Supporting scripts |
| R/RStudio | Statistical analysis and visualization |

## Demonstration to Professor

1. **Show Dataset**: Display the social media dataset structure
2. **HDFS Upload**: Demonstrate uploading data to HDFS
3. **Hive Queries**: Run SQL queries to show basic analysis
4. **PySpark Processing**: Execute trend analysis and sentiment analysis
5. **Export Results**: Show CSV outputs from PySpark
6. **R Visualizations**: Display generated charts and dashboard
7. **Final Dashboard**: Present the complete trend analysis dashboard

## Troubleshooting

### HDFS Issues
- Ensure Hadoop is running: `start-dfs.sh`
- Check HDFS status: `hdfs dfs -ls /`

### Hive Issues
- Ensure Hive metastore is initialized
- Check Hive connection: `hive -e "SHOW DATABASES;"`

### PySpark Issues
- Ensure Spark is properly configured with Hive support
- Check Python dependencies: `pip install textblob`

### R Issues
- Install required packages: `Rscript install_packages.R`
- Check R version compatibility (R 3.6+ recommended)

## Future Enhancements

- Real-time data streaming with Spark Streaming
- Machine learning models for trend prediction
- Interactive dashboard with Shiny
- Integration with actual social media APIs
- Advanced NLP for topic modeling
- Geospatial analysis of trends

## License

This project is created for educational purposes.

## Author

Social Media Trend Analysis Project
Big Data Analytics Course
