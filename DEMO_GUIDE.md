# Social Media Trend Analysis - Demo Guide for Professor

## Project Overview
This project demonstrates **Big Data processing** using:
- **Hadoop** (HDFS for distributed storage)
- **PySpark** (Apache Spark for data processing)
- **R** (Data visualization)

The project analyzes social media posts to find trending hashtags, platform engagement, and daily activity patterns.

---

## Quick Demo (5-10 minutes)

### Step 1: Show Project Structure
Open the project folder in Windows Explorer and show:
```
Social_Media_Trend_Analysis/
├── dataset/
│   └── social_media.csv          # Sample dataset (50 posts)
├── pyspark-scripts/
│   ├── trend_analysis.py         # Main PySpark analysis script
│   └── output/                   # Analysis results (CSV files)
├── r-scripts/
│   └── visualizations.R          # R visualization script
└── README.md                     # Project documentation
```

**Say:** "This is the project structure. We have a sample social media dataset, PySpark scripts for analysis, and R scripts for visualization."

---

### Step 2: Show the Dataset
Open `dataset/social_media.csv` in Excel or any text editor.

**Show the columns:**
- id, date, platform, user, text, hashtags, likes, shares, comments

**Say:** "This is our sample dataset with 50 social media posts from Twitter and Instagram with engagement metrics."

---

### Step 3: Show Hadoop is Running
Open WSL2 terminal and run:
```bash
jps
```

**Expected output:**
```
NameNode
DataNode
SecondaryNameNode
```

**Say:** "Hadoop HDFS is running. This provides distributed storage for big data processing."

---

### Step 4: Show PySpark Analysis Script
Open `pyspark-scripts/trend_analysis.py` in VS Code or any editor.

**Highlight key sections:**
- Line 14-17: Spark session initialization
- Line 24: Loading CSV data
- Line 31-77: Hashtag trend analysis
- Line 84-99: Platform analysis
- Line 116-132: Daily trend analysis

**Say:** "This PySpark script loads the CSV data and performs 5 different analyses: hashtag trends, platform comparison, top posts, daily trends, and user engagement."

---

### Step 5: Run PySpark Analysis (Live Demo)
In WSL2 terminal:
```bash
cd /mnt/d/Projects/Social_Media_Trend_Analysis/pyspark-scripts
spark-submit trend_analysis.py
```

**Watch the output:**
- "Spark Session created successfully"
- "Total records loaded: 50"
- Analysis results for each section
- "Analysis completed successfully!"

**Say:** "Now I'm running the PySpark analysis. It processes the data using Apache Spark's distributed computing engine."

---

### Step 6: Show Analysis Results
Open the output CSV files in `pyspark-scripts/output/` folder:

**Open `hashtag_analysis.csv/part-00000-*.csv`:**
- Shows trending hashtags with engagement metrics
- Columns: hashtag, post_count, avg_likes, avg_shares, avg_comments, total_engagement, trend_score

**Say:** "These are the analysis results. This file shows which hashtags are trending based on engagement. #News has the highest trend score of 0.87."

**Open `platform_analysis.csv/part-00000-*.csv`:**
- Shows comparison between Twitter and Instagram

**Say:** "This shows platform comparison - which platform has more engagement."

**Open `daily_trends.csv/part-00000-*.csv`:**
- Shows daily activity patterns

**Say:** "This shows how engagement varies day by day."

---

### Step 7: Show R Visualization Script (Optional)
Open `r-scripts/visualizations.R` in editor.

**Say:** "We also have R scripts to create visualizations from these results. This generates charts and graphs for better data understanding."

---

## What to Explain to Professor

### 1. **Technology Stack**
- **Hadoop**: Distributed storage framework for big data
- **PySpark**: Apache Spark's Python API for distributed data processing
- **R**: Statistical computing and visualization

### 2. **Why This Project?**
- Demonstrates end-to-end big data pipeline
- Shows real-world social media analytics
- Uses industry-standard tools (Hadoop, Spark)
- Scalable to millions of posts

### 3. **Key Features**
- Hashtag trend detection
- Platform engagement comparison
- Daily activity analysis
- User engagement metrics
- Trend scoring algorithm

### 4. **How It Works**
```
CSV Data → PySpark Processing → Analysis Results → Visualizations
```

---

## Quick Reference Commands

### Start Hadoop (if stopped)
```bash
start-dfs.sh
```

### Check Hadoop status
```bash
jps
```

### Run PySpark analysis
```bash
cd /mnt/d/Projects/Social_Media_Trend_Analysis/pyspark-scripts
spark-submit trend_analysis.py
```

### View results
```bash
cd output
ls
```

---

## Troubleshooting

### If Hadoop is not running:
```bash
start-dfs.sh
```

### If PySpark gives Java error:
```bash
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
```

### If output folder is empty:
Run the PySpark script again to generate results.

---

## Summary for Professor

**This project demonstrates:**
1. ✅ Big Data storage with Hadoop HDFS
2. ✅ Distributed data processing with PySpark
3. ✅ Social media trend analysis
4. ✅ Data visualization with R
5. ✅ Scalable architecture (can handle millions of records)

**The analysis shows:**
- Most trending hashtags (#News, #Food, #Finance)
- Platform engagement patterns
- Daily activity trends
- Top performing posts
- User engagement metrics

**All results are saved as CSV files for further analysis or visualization.**
