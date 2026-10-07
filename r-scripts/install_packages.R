# Install Required R Packages for Social Media Trend Analysis
# Run this script in R or RStudio to install all required packages

# List of required packages
required_packages <- c("ggplot2", "dplyr", "gridExtra", "scales")

# Function to install packages if not already installed
install_if_missing <- function(package) {
  if (!require(package, character.only = TRUE, quietly = TRUE)) {
    cat(paste("Installing package:", package, "\n"))
    install.packages(package, dependencies = TRUE, lib = "~/R/library")
  } else {
    cat(paste("Package already installed:", package, "\n"))
  }
}

# Create user library directory
dir.create("~/R/library", showWarnings = FALSE, recursive = TRUE)
.libPaths("~/R/library")

# Install all required packages
cat("Installing required R packages...\n")
cat("================================\n")

for (pkg in required_packages) {
  install_if_missing(pkg)
}

cat("\n================================\n")
cat("All packages installed successfully!\n")
cat("\nYou can now run the visualization script.\n")
