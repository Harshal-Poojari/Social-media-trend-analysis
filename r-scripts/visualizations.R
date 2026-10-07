# Social Media Trend Analysis - R Visualization Script
# This script creates visualizations from PySpark output data

# Set user library path
.libPaths("~/R/library")

# Load required libraries
library(ggplot2)
library(dplyr)
library(gridExtra)
library(scales)

# Set working directory to project root
setwd("../ output")

# Function to read CSV files safely
read_csv_safe <- function(filename) {
  if (file.exists(filename)) {
    return(read.csv(filename))
  } else {
    warning(paste("File not found:", filename))
    return(NULL)
  }
}

# Read data from PySpark output
hashtag_data <- read_csv_safe("hashtag_analysis.csv/part-00000-*.csv")
platform_data <- read_csv_safe("platform_analysis.csv/part-00000-*.csv")
daily_data <- read_csv_safe("daily_trends.csv/part-00000-*.csv")
sentiment_data <- read_csv_safe("sentiment_distribution.csv/part-00000-*.csv")
sentiment_engagement <- read_csv_safe("sentiment_engagement.csv/part-00000-*.csv")

# Create output directory for plots
dir.create("plots", showWarnings = FALSE)

# Visualization 1: Top Trending Hashtags
if (!is.null(hashtag_data)) {
  top_hashtags <- hashtag_data %>%
    arrange(desc(post_count)) %>%
    head(10)
  
  p1 <- ggplot(top_hashtags, aes(x = reorder(hashtag, post_count), y = post_count)) +
    geom_col(fill = "#FF6B6B") +
    coord_flip() +
    labs(
      title = "Top 10 Trending Hashtags",
      subtitle = "By number of posts",
      x = "Hashtag",
      y = "Number of Posts"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      axis.text = element_text(size = 10)
    )
  
  ggsave("plots/top_hashtags.png", p1, width = 10, height = 6, dpi = 300)
  print(p1)
}

# Visualization 2: Hashtag Trend Score
if (!is.null(hashtag_data)) {
  top_trends <- hashtag_data %>%
    arrange(desc(trend_score)) %>%
    head(10)
  
  p2 <- ggplot(top_trends, aes(x = reorder(hashtag, trend_score), y = trend_score)) +
    geom_col(fill = "#4ECDC4") +
    coord_flip() +
    labs(
      title = "Top 10 Hashtags by Trend Score",
      subtitle = "Trend Score = Frequency (0.4) + Engagement (0.4) + Growth (0.2)",
      x = "Hashtag",
      y = "Trend Score"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      axis.text = element_text(size = 10)
    )
  
  ggsave("plots/trend_score.png", p2, width = 10, height = 6, dpi = 300)
  print(p2)
}

# Visualization 3: Platform Comparison
if (!is.null(platform_data)) {
  p3 <- ggplot(platform_data, aes(x = platform, y = total_engagement, fill = platform)) +
    geom_col() +
    labs(
      title = "Total Engagement by Platform",
      subtitle = "Likes + Shares + Comments",
      x = "Platform",
      y = "Total Engagement"
    ) +
    scale_y_continuous(labels = comma) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      legend.position = "none"
    ) +
    scale_fill_brewer(palette = "Set2")
  
  ggsave("plots/platform_engagement.png", p3, width = 8, height = 6, dpi = 300)
  print(p3)
}

# Visualization 4: Average Engagement by Platform
if (!is.null(platform_data)) {
  p4 <- ggplot(platform_data, aes(x = platform, y = avg_engagement, fill = platform)) +
    geom_col() +
    labs(
      title = "Average Engagement per Post by Platform",
      subtitle = "Average Likes + Shares + Comments",
      x = "Platform",
      y = "Average Engagement"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      legend.position = "none"
    ) +
    scale_fill_brewer(palette = "Set3")
  
  ggsave("plots/avg_platform_engagement.png", p4, width = 8, height = 6, dpi = 300)
  print(p4)
}

# Visualization 5: Daily Trends
if (!is.null(daily_data)) {
  daily_data$date <- as.Date(daily_data$date)
  
  p5 <- ggplot(daily_data, aes(x = date, y = post_count)) +
    geom_line(color = "#45B7D1", size = 1.5) +
    geom_point(color = "#45B7D1", size = 3) +
    labs(
      title = "Daily Post Volume",
      subtitle = "Number of posts per day",
      x = "Date",
      y = "Number of Posts"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      axis.text.x = element_text(angle = 45, hjust = 1)
    )
  
  ggsave("plots/daily_volume.png", p5, width = 10, height = 6, dpi = 300)
  print(p5)
}

# Visualization 6: Daily Engagement Trends
if (!is.null(daily_data)) {
  daily_data$date <- as.Date(daily_data$date)
  
  p6 <- ggplot(daily_data, aes(x = date, y = total_engagement)) +
    geom_line(color = "#96CEB4", size = 1.5) +
    geom_point(color = "#96CEB4", size = 3) +
    labs(
      title = "Daily Engagement Trends",
      subtitle = "Total engagement per day",
      x = "Date",
      y = "Total Engagement"
    ) +
    scale_y_continuous(labels = comma) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      axis.text.x = element_text(angle = 45, hjust = 1)
    )
  
  ggsave("plots/daily_engagement.png", p6, width = 10, height = 6, dpi = 300)
  print(p6)
}

# Visualization 7: Sentiment Distribution
if (!is.null(sentiment_data)) {
  sentiment_data$sentiment <- factor(sentiment_data$sentiment, 
                                     levels = c("positive", "neutral", "negative"))
  
  p7 <- ggplot(sentiment_data, aes(x = sentiment, y = count, fill = sentiment)) +
    geom_col() +
    labs(
      title = "Sentiment Distribution",
      subtitle = "Number of posts by sentiment",
      x = "Sentiment",
      y = "Count"
    ) +
    scale_fill_manual(values = c("positive" = "#2ECC71", 
                                 "neutral" = "#95A5A6", 
                                 "negative" = "#E74C3C")) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      legend.position = "none"
    )
  
  ggsave("plots/sentiment_distribution.png", p7, width = 8, height = 6, dpi = 300)
  print(p7)
}

# Visualization 8: Engagement by Sentiment
if (!is.null(sentiment_engagement)) {
  sentiment_engagement$sentiment <- factor(sentiment_engagement$sentiment, 
                                           levels = c("positive", "neutral", "negative"))
  
  p8 <- ggplot(sentiment_engagement, aes(x = sentiment, y = avg_engagement, fill = sentiment)) +
    geom_col() +
    labs(
      title = "Average Engagement by Sentiment",
      subtitle = "Average likes + shares + comments",
      x = "Sentiment",
      y = "Average Engagement"
    ) +
    scale_fill_manual(values = c("positive" = "#2ECC71", 
                                 "neutral" = "#95A5A6", 
                                 "negative" = "#E74C3C")) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      legend.position = "none"
    )
  
  ggsave("plots/engagement_by_sentiment.png", p8, width = 8, height = 6, dpi = 300)
  print(p8)
}

# Visualization 9: Hashtag Engagement Analysis
if (!is.null(hashtag_data)) {
  top_engagement <- hashtag_data %>%
    arrange(desc(total_engagement)) %>%
    head(10)
  
  p9 <- ggplot(top_engagement, aes(x = reorder(hashtag, total_engagement), y = total_engagement)) +
    geom_col(fill = "#9B59B6") +
    coord_flip() +
    labs(
      title = "Top 10 Hashtags by Total Engagement",
      subtitle = "Likes + Shares + Comments",
      x = "Hashtag",
      y = "Total Engagement"
    ) +
    scale_x_continuous(labels = comma) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      axis.text = element_text(size = 10)
    )
  
  ggsave("plots/hashtag_engagement.png", p9, width = 10, height = 6, dpi = 300)
  print(p9)
}

# Visualization 10: Dashboard - Combined View
if (!is.null(hashtag_data) && !is.null(platform_data) && !is.null(sentiment_data)) {
  # Create a multi-panel dashboard
  p_a <- ggplot(hashtag_data %>% arrange(desc(post_count)) %>% head(5), 
                aes(x = reorder(hashtag, post_count), y = post_count)) +
    geom_col(fill = "#FF6B6B") +
    coord_flip() +
    labs(title = "Top Hashtags", x = "", y = "") +
    theme_minimal() +
    theme(plot.title = element_text(size = 12, face = "bold"))
  
  p_b <- ggplot(platform_data, aes(x = platform, y = total_engagement, fill = platform)) +
    geom_col() +
    labs(title = "Platform Engagement", x = "", y = "") +
    theme_minimal() +
    theme(legend.position = "none", plot.title = element_text(size = 12, face = "bold")) +
    scale_fill_brewer(palette = "Set2")
  
  p_c <- ggplot(sentiment_data, aes(x = sentiment, y = count, fill = sentiment)) +
    geom_col() +
    labs(title = "Sentiment", x = "", y = "") +
    scale_fill_manual(values = c("positive" = "#2ECC71", 
                                 "neutral" = "#95A5A6", 
                                 "negative" = "#E74C3C")) +
    theme_minimal() +
    theme(legend.position = "none", plot.title = element_text(size = 12, face = "bold"))
  
  dashboard <- grid.arrange(p_a, p_b, p_c, ncol = 3, 
                           top = "Social Media Trend Analysis Dashboard")
  
  ggsave("plots/dashboard.png", dashboard, width = 14, height = 5, dpi = 300)
  print(dashboard)
}

cat("\nAll visualizations created successfully!\n")
cat("Plots saved in: plots/ directory\n")
