# Ubuntu Setup Guide for Social Media Trend Analysis Project

This guide provides step-by-step instructions for setting up the complete environment on Ubuntu (including WSL2 on Windows) for the Social Media Trend Analysis project.

## Table of Contents

1. [Ubuntu Installation](#ubuntu-installation)
2. [Java Installation](#java-installation)
3. [Hadoop Installation](#hadoop-installation)
4. [Hive Installation](#hive-installation)
5. [Python and PySpark Installation](#python-and-pyspark-installation)
6. [R and RStudio Installation](#r-and-rstudio-installation)
7. [Project Setup](#project-setup)
8. [Verification](#verification)

---

## Ubuntu Installation

### Option 1: WSL2 on Windows (Recommended)

1. Open PowerShell as Administrator
2. Run the following command:
   ```powershell
   wsl --install
   ```
3. Restart your computer
4. After restart, Ubuntu will install automatically
5. Set up your Ubuntu username and password
6. Update Ubuntu:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### Option 2: Native Ubuntu Installation

If you're installing Ubuntu directly on a machine or VM, download the latest LTS version from [ubuntu.com](https://ubuntu.com/download/desktop) and follow the installation wizard.

---

## Java Installation

Hadoop requires Java 8 or higher. OpenJDK 8 is recommended.

### Install OpenJDK 8

```bash
sudo apt update
sudo apt install openjdk-8-jdk -y
```

### Set JAVA_HOME Environment Variable

```bash
# Find Java installation path
readlink -f $(which java)

# Edit .bashrc file
nano ~/.bashrc

# Add the following lines at the end (adjust path if needed)
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin

# Save and exit (Ctrl+X, Y, Enter)

# Reload .bashrc
source ~/.bashrc

# Verify installation
java -version
echo $JAVA_HOME
```

---

## Hadoop Installation

### Step 1: Download Hadoop

```bash
# Create directory for Hadoop
sudo mkdir -p /usr/local/hadoop

# Download Hadoop 3.3.4 (or latest stable version)
cd /tmp
wget https://downloads.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz

# Extract to installation directory
sudo tar -xzf hadoop-3.3.4.tar.gz -C /usr/local/hadoop --strip-components=1

# Change ownership
sudo chown -R $USER:$USER /usr/local/hadoop
```

### Step 2: Configure Hadoop Environment Variables

```bash
nano ~/.bashrc
```

Add the following lines:

```bash
# Hadoop Environment Variables
export HADOOP_HOME=/usr/local/hadoop
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
```

Save and reload:

```bash
source ~/.bashrc
```

### Step 3: Configure Hadoop

```bash
cd /usr/local/hadoop/etc/hadoop
```

#### Edit `hadoop-env.sh`

```bash
nano hadoop-env.sh
```

Add or modify:

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

#### Edit `core-site.xml`

```bash
nano core-site.xml
```

Replace with:

```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
```

#### Edit `hdfs-site.xml`

```bash
nano hdfs-site.xml
```

Replace with:

```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///usr/local/hadoop/store/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///usr/local/hadoop/store/hdfs/datanode</value>
    </property>
</configuration>
```

#### Create necessary directories

```bash
sudo mkdir -p /usr/local/hadoop/store/hdfs/namenode
sudo mkdir -p /usr/local/hadoop/store/hdfs/datanode
sudo chown -R $USER:$USER /usr/local/hadoop/store
```

#### Edit `mapred-site.xml`

```bash
nano mapred-site.xml
```

Replace with:

```xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
</configuration>
```

#### Edit `yarn-site.xml`

```bash
nano yarn-site.xml
```

Replace with:

```xml
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services.mapreduce_shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
</configuration>
```

### Step 4: Setup SSH

```bash
# Install SSH
sudo apt install openssh-server -y

# Generate SSH keys
ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa

# Add to authorized keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# Test SSH connection
ssh localhost
```

### Step 5: Format HDFS and Start Hadoop

```bash
# Format namenode (only do this once!)
hdfs namenode -format

# Start HDFS
start-dfs.sh

# Start YARN
start-yarn.sh

# Verify Hadoop is running
jps
```

You should see: NameNode, DataNode, SecondaryNameNode, ResourceManager, NodeManager

### Step 6: Test Hadoop

```bash
# Create a test directory
hdfs dfs -mkdir /test

# List HDFS directories
hdfs dfs -ls /

# Stop Hadoop (when needed)
stop-dfs.sh
stop-yarn.sh
```

---

## Hive Installation

### Step 1: Download Hive

```bash
# Create directory for Hive
sudo mkdir -p /usr/local/hive

# Download Hive 3.1.3
cd /tmp
wget https://downloads.apache.org/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz

# Extract to installation directory
sudo tar -xzf apache-hive-3.1.3-bin.tar.gz -C /usr/local/hive --strip-components=1

# Change ownership
sudo chown -R $USER:$USER /usr/local/hive
```

### Step 2: Configure Hive Environment Variables

```bash
nano ~/.bashrc
```

Add:

```bash
# Hive Environment Variables
export HIVE_HOME=/usr/local/hive
export PATH=$PATH:$HIVE_HOME/bin
export HADOOP_HOME=/usr/local/hadoop
```

Save and reload:

```bash
source ~/.bashrc
```

### Step 3: Download and Setup Hadoop Common

```bash
cd /usr/local/hive/lib
wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar
```

### Step 4: Configure Hive

```bash
cd /usr/local/hive/conf
```

#### Create `hive-site.xml`

```bash
nano hive-site.xml
```

Add:

```xml
<configuration>
    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:derby:;databaseName=/usr/local/hive/metastore_db;create=true</value>
    </property>
    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>org.apache.derby.jdbc.EmbeddedDriver</value>
    </property>
    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
    </property>
    <property>
        <name>hive.exec.scratchdir</name>
        <value>/tmp/hive</value>
    </property>
</configuration>
```

### Step 5: Initialize Hive Metastore

```bash
# Create HDFS directories for Hive
hdfs dfs -mkdir -p /tmp/hive
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -chmod g+w /tmp/hive
hdfs dfs -chmod g+w /user/hive/warehouse

# Initialize metastore
schematool -dbType derby -initSchema
```

### Step 6: Test Hive

```bash
# Start Hive CLI
hive

# Test query
CREATE DATABASE test_db;
SHOW DATABASES;
USE test_db;
CREATE TABLE test (id INT);
DROP TABLE test;
DROP DATABASE test_db;
EXIT;
```

---

## Python and PySpark Installation

### Step 1: Install Python 3 and pip

```bash
sudo apt update
sudo apt install python3 python3-pip -y

# Verify installation
python3 --version
pip3 --version
```

### Step 2: Install PySpark

```bash
pip3 install pyspark
```

### Step 3: Install Required Python Libraries

```bash
pip3 install textblob
python3 -m textblob.download_corpora
```

### Step 4: Verify PySpark

```bash
python3 -c "from pyspark.sql import SparkSession; print('PySpark installed successfully')"
```

### Step 5: Configure PySpark with Hive Support

PySpark should automatically detect Hive if configured correctly. Test with:

```bash
python3 << EOF
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .appName("Test") \
    .enableHiveSupport() \
    .getOrCreate()
print("Spark with Hive support: OK")
spark.stop()
EOF
```

---

## R and RStudio Installation

### Step 1: Install R

```bash
sudo apt update
sudo apt install r-base r-base-dev -y

# Verify installation
R --version
```

### Step 2: Install RStudio Desktop (Optional)

```bash
# Download RStudio
cd /tmp
wget https://download1.rstudio.org/electron/focal/amd64/rstudio-2023.06.0-421-amd64.deb

# Install
sudo dpkg -i rstudio-*.deb

# Fix dependencies if needed
sudo apt install -f
```

### Step 3: Install Required R Packages

```bash
# Navigate to project directory
cd /path/to/Social_Media_Trend_Analysis/r-scripts

# Run the package installation script
Rscript install_packages.R
```

Or manually in R:

```r
install.packages(c("ggplot2", "dplyr", "gridExtra", "scales"))
```

### Step 4: Verify R Installation

```bash
Rscript -e "library(ggplot2); print('R packages installed successfully')"
```

---

## Project Setup

### Step 1: Copy Project Files

```bash
# Navigate to your project directory
cd /path/to/Social_Media_Trend_Analysis

# Make scripts executable
chmod +x hadoop-scripts/*.sh
chmod +x pyspark-scripts/*.py
```

### Step 2: Start Hadoop Services

```bash
start-dfs.sh
start-yarn.sh

# Verify
jps
```

### Step 3: Setup HDFS for Project

```bash
cd hadoop-scripts
./setup_hdfs.sh
```

### Step 4: Create Hive Table

```bash
cd ../hive-scripts
hive -f create_table.hql
```

### Step 5: Run PySpark Analysis

```bash
cd ../pyspark-scripts
spark-submit trend_analysis.py
```

### Step 6: Run R Visualizations

```bash
cd ../r-scripts
Rscript visualizations.R
```

---

## Verification

### Check All Services

```bash
# Check Hadoop services
jps

# Expected output:
# NameNode
# DataNode
# SecondaryNameNode
# ResourceManager
# NodeManager
```

### Test HDFS

```bash
hdfs dfs -ls /
hdfs dfs -ls /socialmedia
```

### Test Hive

```bash
hive -e "SHOW DATABASES;"
hive -e "USE social_media; SELECT COUNT(*) FROM posts;"
```

### Test PySpark

```bash
cd pyspark-scripts
spark-submit trend_analysis.py
```

### Test R

```bash
cd r-scripts
Rscript visualizations.R
```

---

## Troubleshooting

### Hadoop Issues

**Problem: NameNode not starting**
- Solution: Check logs in `/usr/local/hadoop/logs/`
- Reformat namenode: `hdfs namenode -format` (WARNING: This deletes all data)

**Problem: Permission denied errors**
- Solution: Ensure proper ownership: `sudo chown -R $USER:$USER /usr/local/hadoop`

### Hive Issues

**Problem: Metastore connection error**
- Solution: Reinitialize metastore: `schematool -dbType derby -initSchema`

**Problem: HDFS directory not found**
- Solution: Create HDFS directories:
  ```bash
  hdfs dfs -mkdir -p /tmp/hive
  hdfs dfs -mkdir -p /user/hive/warehouse
  ```

### PySpark Issues

**Problem: Hive support not working**
- Solution: Ensure `hive-site.xml` is in Spark's configuration directory
- Copy Hive config to Spark: `cp /usr/local/hive/conf/hive-site.xml $SPARK_HOME/conf/`

### R Issues

**Problem: Package installation fails**
- Solution: Install system dependencies:
  ```bash
  sudo apt install libcurl4-openssl-dev libssl-dev libxml2-dev -y
  ```

---

## Next Steps

After completing the setup:

1. Review the [README.md](README.md) for project usage
2. Run the sample analysis with the provided dataset
3. Customize the analysis for your specific requirements
4. Replace the sample dataset with real social media data if available

---

## Additional Resources

- [Hadoop Documentation](https://hadoop.apache.org/docs/)
- [Hive Documentation](https://cwiki.apache.org/confluence/display/Hive/Home)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)
- [R Documentation](https://www.r-project.org/)
- [ggplot2 Documentation](https://ggplot2.tidyverse.org/)

---

## System Requirements

- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 20GB minimum
- **OS**: Ubuntu 18.04+ or WSL2 on Windows 10/11
- **Processor**: 64-bit processor

---

## Notes

- This guide uses single-node Hadoop setup, suitable for development and learning
- For production, consider multi-node cluster setup
- Derby database is used for Hive metastore (suitable for single-user development)
- WSL2 users may need to configure additional network settings for external access
