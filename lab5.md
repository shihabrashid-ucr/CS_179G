



# CS 179G Lab 5

## (Re)install Spark

### 1. Configure SSH to localhost
Create a SSH key pair and add them the localhost 
```bash
if [[ ! -f ~/.ssh/id_rsa ]]; then
  ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
fi
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
# Type "yes" if promoted
ssh localhost "exit"
```

### 2. Install  [Apache Spark](https://spark.apache.org/)
Download the archive of  [Spark](https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz), or run the following commands
```bash
cd ~
# Download and unarchive Spark
if [[ ! -f ~/spark-3.3.1-bin-hadoop3.tgz ]]; then
  wget https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz
fi
tar xf spark-3.3.1-bin-hadoop3.tgz
```

### 3. Set environment variables
#### 3.1 Remove obsolete environment variables
If you had set variable `SPARK_HOME` and `PYSPARK_PYTHON` before, remove them from `~/.bashrc`.

#### 3.2 Add environment variables for Hadoop and Spark
Run the following commands
```bash
echo "export SPARK_HOME=\"/home/ubuntu/spark-3.3.1-bin-hadoop3\"" >> ~/.bashrc
echo "export PATH=\$PATH:\"\$SPARK_HOME\"/bin" >> ~/.bashrc
source ~/.bashrc
```

### 4. Configure Spark
Reference: [https://mallikarjuna_g.gitbooks.io/spark/content/spark-standalone-example-2-workers-on-1-node-cluster.html](https://mallikarjuna_g.gitbooks.io/spark/content/spark-standalone-example-2-workers-on-1-node-cluster.html)

#### 5.1 Edit *~/spark/spark-3.3.1-bin-hadoop3/conf/spark-env.sh*
Make a copy of the template file
```bash
cp ~/spark-3.3.1-bin-hadoop3/conf/spark-env.sh.template ~/spark-3.3.1-bin-hadoop3/conf/spark-env.sh
```
Edit ***~/spark-3.3.1-bin-hadoop3/conf/spark-env.sh***
```bash
SPARK_MASTER_HOST="127.0.0.1"
SPARK_WORKER_CORES=1
SPARK_WORKER_MEMORY="1g"
SPARK_WORKER_INSTANCES=2

export PYSPARK_DRIVER_PYTHON="/home/ubuntu/YOUR_VENV/bin/python3"
export PYSPARK_PYTHON="/home/ubuntu/YOUR_VENV/bin/python3"
```

#### Start Spark's master and workers
Run
```bash
$SPARK_HOME/sbin/start-all.sh
```

You should see something like
```
starting org.apache.spark.deploy.master.Master, logging to /home/ubuntu/spark-3.3.1-bin-hadoop3/logs/spark-ubuntu-org.apache.spark.deploy.master.Master-1-ip-#-#-#-#.out
localhost: starting org.apache.spark.deploy.worker.Worker, logging to /home/ubuntu/spark-3.3.1-bin-hadoop3/logs/spark-ubuntu-org.apache.spark.deploy.worker.Worker-1-ip-#-#-#-#.out
localhost: starting org.apache.spark.deploy.worker.Worker, logging to /home/ubuntu/spark-3.3.1-bin-hadoop3/logs/spark-ubuntu-org.apache.spark.deploy.worker.Worker-2-ip-#-#-#-#.out
```

#### Stop Spark
```bash
$SPARK_HOME/sbin/stop-all.sh
```

#### Change number of workers
1. ```bash
	$SPARK_HOME/sbin/stop-all.sh
	```
2. Change `SPARK_WORKER_INSTANCES` in ***spark-env.sh***
3. ```bash
	$SPARK_HOME/sbin/start-all.sh
	``` 

## Test Spark
Create a Python script with the following content
```python
import os
import sys

from pyspark import SparkContext

# Check if Python is from the virtual environment
print(f"Python interpreter: {sys.executable}")
print()

# Spark standalone cluster
MASTER_URL = "spark://localhost:7077"

# Locally with 1 thread
# MASTER_URL = "local"

# Locally with 2 threads
# MASTER_URL = "local[2]"

# Create Spark context
sc = SparkContext(MASTER_URL, "Word Count Example")

# Read a text file and count words in lower case
words = sc.textFile(os.path.join(os.getenv("SPARK_HOME"), "NOTICE")).flatMap(
    lambda line: filter(None, line.lower().split(" ")))

# Reduce
wordCounts = words.map(lambda w: (w, 1)).reduceByKey(lambda a, b: a + b)

# Get and sort results in descending order
output = wordCounts.collect()
output.sort(key=lambda wc: wc[1], reverse=True)

# Print the 5 most frequent words
for (word, count) in output[:5]:
    print(f"{word}: {count}")
```

Save it as ***~/word_count.py***

Then, run
```bash
# 2>/dev/null suppresses messages from Spark printed to stderr
time spark-submit ~/word_count.py 2>/dev/null
```

The output should have something like this, which is the running [time](https://linuxize.com/post/linux-time-command/) of the program
```
Python interpreter: /home/ubuntu/venv/bin/python3

the: 441
apache: 205
software: 192
of: 165
copyright: 142

real    0m13.904s
user    0m9.251s
sys     0m0.612s
```

## Task
Test your code with:
- Different data size (small, medium, large, etc.)
- Different master (standalone, locally with single thread or multiple threads, etc.) 
