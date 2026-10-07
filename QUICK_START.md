# Quick Start Guide - Social Media Trend Analysis

This guide shows you how to run the project step-by-step.

## Prerequisites

You must have Ubuntu (or WSL2 on Windows) with the following installed:
- Java 8+
- Hadoop (single-node)
- Apache Hive
- Python 3 + PySpark
- R/RStudio

**If you haven't installed these yet, follow `UBUNTU_SETUP.md` first.**

---

## Step-by-Step Execution

### Step 1: Start Hadoop Services

```bash
# Start HDFS
start-dfs.sh

# Start YARN
start-yarn.sh

# Verify services are running
jps
```

Expected output should include: NameNode, DataNode, ResourceManager, NodeManager

---

### Step 2: Setup HDFS and Upload Dataset

```bash
cd /path/to/Social_Media_Trend_Analysis/hadoop-scripts

# Make script executable
chmod +x setup_hdfs.sh

# Run setup
./setup_hdfs.sh
```

This will:
- Create `/socialmedia` directory in HDFS
- Upload `social_media.csv` to HDFS

---

### Step 3: Create Hive Table

```bash
cd ../hive-scripts

# Run Hive table creation script
hive -f create_table.hql
```

This will:
- Create `social_media` database
- Create `posts` table
- Load data from HDFS

---

### Step 4: Run Hive Analysis Queries (Optional)

```bash
# Run all analysis queries
hive -f analysis_queries.hql
```

Or run individual queries in Hive CLI:

```bash
hive
USE social_media;

# Most popular hashtags
SELECT hashtag, COUNT(*) AS count FROM posts GROUP BY hashtag ORDER BY count DESC;

# Highest engagement posts
SELECT id, hashtag, likes + shares + comments AS engagement 
FROM posts ORDER BY engagement DESC LIMIT 10;

EXIT;
```

---

### Step 5: Run PySpark Trend Analysis

```bash
cd ../pyspark-scripts

# Install TextBlob for sentiment analysis (if not installed)
pip3 install textblob
python3 -m textblob.download_corpora

# Run trend analysis
spark-submit trend_analysis.py
```

This will:
- Load data from Hive
- Calculate hashtag statistics
- Compute trend scores
- Analyze platforms and daily trends
- Save results to `output/` directory

---

### Step 6: Run PySpark Sentiment Analysis (Optional)

```bash
# Run sentiment analysis
spark-submit sentiment_analysis.py
```

This will:
- Analyze sentiment of each post
- Classify as positive/negative/neutral
- Generate sentiment statistics
- Save results to `output/` directory

---

### Step 7: Generate R Visualizations

```bash
cd ../r-scripts

# Install required R packages (first time only)
Rscript install_packages.R

# Run visualizations
Rscript visualizations.R
```

This will:
- Read PySpark output files
- Generate 10 visualization charts
- Save plots to `output/plots/` directory

---

## Viewing Results

### PySpark Output Files (in `output/` directory)
- `hashtag_analysis.csv` - Hashtag statistics and trend scores
- `platform_analysis.csv` - Platform engagement metrics
- `daily_trends.csv` - Daily activity trends
- `top_posts.csv` - Top performing posts
- `user_analysis.csv` - User engagement statistics

### R Visualizations (in `output/plots/` directory)
- `top_hashtags.png` - Top 10 trending hashtags
- `trend_score.png` - Hashtags by trend score
- `platform_engagement.png` - Platform comparison
- `daily_volume.png` - Daily post volume
- `sentiment_distribution.png` - Sentiment analysis
- `dashboard.png` - Combined dashboard view

---

## Complete Execution Script

You can create a single script to run everything:

```bash
#!/bin/bash

# Start Hadoop
start-dfs.sh
start-yarn.sh
sleep 10

# Setup HDFS
cd hadoop-scripts
./setup_hdfs.sh

# Create Hive table
cd ../hive-scripts
hive -f create_table.hql

# Run PySpark analysis
cd ../pyspark-scripts
spark-submit trend_analysis.py

# Run R visualizations
cd ../r-scripts
Rscript visualizations.R

echo "Analysis complete! Check output/ directory for results."
```

Save as `run_analysis.sh`, make executable, and run:

```bash
chmod +x run_analysis.sh
./run_analysis.sh
```

---

## Stopping Services

When done, stop Hadoop services:

```bash
stop-yarn.sh
stop-dfs.sh
```

---

## Troubleshooting

### Hadoop not starting
```bash
# Check if Hadoop is already running
jps

# If NameNode is missing, format it (WARNING: deletes data)
hdfs namenode -format
```

### Hive connection error
```bash
# Ensure HDFS is running
start-dfs.sh

# Reinitialize Hive metastore
schematool -dbType derby -initSchema
```

### PySpark Hive support not working
```bash
# Copy Hive config to Spark
cp /usr/local/hive/conf/hive-site.xml $SPARK_HOME/conf/
```

### R package installation fails
```bash
# Install system dependencies
sudo apt install libcurl4-openssl-dev libssl-dev libxml2-dev -y
```

---

## Demonstration Flow for Professor

1. **Show dataset structure**
   ```bash
   head -5 dataset/social_media.csv
   ```

2. **Show HDFS upload**
   ```bash
   hdfs dfs -ls /socialmedia
   ```

3. **Run Hive query**
   ```bash
   hive -e "USE social_media; SELECT COUNT(*) FROM posts;"
   ```

4. **Run PySpark analysis**
   ```bash
   cd pyspark-scripts
   spark-submit trend_analysis.py
   ```

5. **Show PySpark output**
   ```bash
   cat output/hashtag_analysis.csv/part-00000-*.csv | head -10
   ```

6. **Generate R visualizations**
   ```bash
   cd r-scripts
   Rscript visualizations.R
   ```

7. **Display final dashboard**
   ```bash
   # Open output/plots/dashboard.png in an image viewer
   ```

---

## Customization

### Using Your Own Dataset

Replace `dataset/social_media.csv` with your own CSV file with the same format:
- Columns: id, date, platform, user, text, hashtags, likes, shares, comments

Then re-run the pipeline from Step 2.

### Modifying Analysis

- **Hive queries**: Edit `hive-scripts/analysis_queries.hql`
- **PySpark analysis**: Edit `pyspark-scripts/trend_analysis.py`
- **R visualizations**: Edit `r-scripts/visualizations.R`

---

## System Requirements

- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 20GB minimum
- **OS**: Ubuntu 18.04+ or WSL2 on Windows 10/11

---

## Support

For detailed installation issues, refer to `UBUNTU_SETUP.md`.
