

# CS 179G Lab

## Install PySpark

1. Install JDK 8
	```bash
	sudo apt-get -y install openjdk-8-jdk
	```

2. Set `JAVA_HOME`
	Add the following line to *~/.bashrc* via command line editor (e.g, `vi`)
	```
	export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
	```
	Or, run the following command
	```bash
	echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ~/.bashrc
	```
3. Install PySpark
	Package *wheel* must be installed first
	```bash
	# In virtual environment
	python3 -m pip install wheel pyspark[sql]
	```
5. Set `SPARK_HOME`
	Add the following line to *~/.bashrc* as well
	```
	export PYSPARK_PYTHON=python3
	export SPARK_HOME=/home/ubuntu/miniconda3/envs/YOUR_ENV/lib/python3.10/site-packages/pyspark
	```
	Or run the following commands
	```bash
	echo "export PYSPARK_PYTHON=python3" >> ~/.bashrc
	echo "export SPARK_HOME=/home/ubuntu/miniconda3/envs/YOUR_ENV/lib/python3.10/site-packages/pyspark" >> ~/.bashrc
	```
6. Reload bash environment, test `JAVA_HOME` and `SPARK_HOME`
	```bash
	source ~/.bashrc
	```
	Test if `JAVA_HOME` is properly set
	```bash
	echo $JAVA_HOME
	# /usr/lib/jvm/java-8-openjdk-amd64
	```
	Test if `SPARK_HOME` is properly set
	```bash
	echo $SPARK_HOME
	# /home/ubuntu/miniconda3/envs/YOUR_ENV/lib/python3.10/site-packages/pyspark
	```

#### Test in Python command line or JupyterLab
Reference: [https://realpython.com/pyspark-intro/#hello-world-in-pyspark](https://realpython.com/pyspark-intro/#hello-world-in-pyspark)
```python
import pyspark

sc = pyspark.SparkContext('local[*]')

txt = sc.textFile('file:////usr/share/doc/python3/copyright')
print(txt.count())

python_lines = txt.filter(lambda line: 'python' in line.lower())
print(python_lines.count())
```

## Install MySQL client
```bash
# In virtual environment
python3 -m pip install mysql-connector-python
```

Enter MySQL as root
```bash
sudo mysql
```

Create an user (replace `your_name` and `some_password` accordingly, you may also replace DATABASE `cs179g`)
```sql
CREATE USER 'your_name'@'localhost' IDENTIFIED BY 'some_password';
CREATE DATABASE cs179g;
GRANT ALL PRIVILEGES ON cs179g.* TO 'your_name'@'localhost';
GRANT RELOAD ON *.* TO 'your_name'@'localhost';
FLUSH PRIVILEGES;
exit;
```

## Obtain `mysql-connector-java`
`mysql-connector-java` is needed for PySpark to connect to MySQL.

1. Go to https://dev.mysql.com/downloads/connector/j/
2. Select Operating System: Ubuntu Linux
3. Download **Ubuntu Linux 20.04 (Architecture Independent), DEB Package**
4. Download the file via **No thanks, just start my download**
5. Transfer the deb file to server
6. Install it via `sudo dpkg -i deb_file_path`

Or, you can just execute the following 2 commands
```bash
# wget to download
wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j_8.0.31-1ubuntu22.04_all.deb -P ~
# dpkg to install
sudo dpkg -i ~/mysql-connector-j_8.0.31-1ubuntu22.04_all.deb
```


#### Test MySQL with PySpark
Reference: [https://towardsdatascience.com/pyspark-mysql-tutorial-fa3f7c26dc7](https://towardsdatascience.com/pyspark-mysql-tutorial-fa3f7c26dc7)

Create a folder called `lab3` using `mkdir lab3` and `cd lab3`
Download 2 test files
```bash
wget https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv -P ~/lab3/files
wget https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-white.csv -P ~/lab3/files
```

Test the following Python script
```python
import pandas as pd
import mysql.connector
from pyspark.sql import SparkSession

# Test CSV file read with Pandas (not required in this project)
red_wines = pd.read_csv("/home/ubuntu/lab3/files/winequality-red.csv", sep=";")
red_wines["is_red"] = 1
white_wines = pd.read_csv("/home/ubuntu/lab3/files/winequality-white.csv", sep=";")
white_wines["is_red"] = 0
all_wines = pd.concat([red_wines, white_wines])
print(all_wines)

# Create a table in MySQL and run a simple SELECT query to verify
db_connection = mysql.connector.connect(user="your_name", password="some_password")
db_cursor = db_connection.cursor()
db_cursor.execute("USE cs179g;")

db_cursor.execute("CREATE TABLE IF NOT EXISTS Wines(fixed_acidity FLOAT, volatile_acidity FLOAT, \
                   citric_acid FLOAT, residual_sugar FLOAT, chlorides FLOAT, \
                   free_so2 FLOAT, total_so2 FLOAT, density FLOAT, pH FLOAT, \
                   sulphates FLOAT, alcohol FLOAT, quality INT, is_red INT);")

wine_tuples = list(all_wines.itertuples(index=False, name=None))
wine_tuples_string = ",".join(["(" + ",".join([str(w) for w in wt]) + ")" for wt in wine_tuples])

db_cursor.execute("INSERT INTO Wines(fixed_acidity, volatile_acidity, citric_acid,\
                   residual_sugar, chlorides, free_so2, total_so2, density, pH,\
                   sulphates, alcohol, quality, is_red) VALUES " + wine_tuples_string + ";")
db_cursor.execute("FLUSH TABLES;")

db_cursor.execute("SELECT * FROM Wines LIMIT 5;")
print(db_cursor.fetchall())

# Test connection to MySQL via PySpark
# /usr/share/java/mysql-connector-java-8.0.26.jar is from mysql-connector-java
spark = SparkSession.builder.config("spark.jars", "/usr/share/java/mysql-connector-j-8.0.31.jar") \
    .master("local").appName("PySpark_MySQL_test").getOrCreate()

wine_df = spark.read.format("jdbc").option("url", "jdbc:mysql://localhost:3306/cs179g") \
    .option("driver", "com.mysql.jdbc.Driver").option("dbtable", "Wines") \
    .option("user", "your_name").option("password", "some_password").load()
print(wine_df)
```
### Read files directly using PySpark
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
spark = SparkSession.builder.master('local[*]').appName('Random').getOrCreate()
red_wine_df = spark.read.csv("/home/ubuntu/lab3/files/winequality-red.csv", sep=";", header=True)

# create a new column with default value 1
red_wine_df = red_wine_df.withColumn("is_red", lit(1))
white_wine_df = spark.read.csv("/home/ubuntu/lab3/files/winequality-white.csv", sep=";", header=True)
white_wine_df = white_wine_df.withColumn("is_red", lit(0))

all_wines = red_wine_df.union(white_wine_df)
```

### Some Common PySpark operations
Select
```python
from pyspark.sql.functions import col
selected_wines = all_wines.select(["fixed acidity", "is_red"])
```
Where
```python
where_example = all_wines.filter(col("free sulfur dioxide") > 15)
all_wines.filter(col("is_red") == 1).count()
```
Group By
```python
grouped_by = all_wines.groupBy("is_red").count()
```
Aggregate functions
Task: Write a code to print the following output:
```
+------+----------+-------------------+--------+
|is_red|sum_sulfur|         avg_citric|max_resi|
+------+----------+-------------------+--------+
|     0|  172939.0|0.33419150673743736|     9.9|
|     1|   25384.0| 0.2709756097560964|       9|
+------+----------+-------------------+--------+
```
Use Google (the most important skill in learning pyspark)
```python

```

#### (Optional) To use MySQL as Django backend, check 
By default, Django uses SQLite3 as its backend database, you may use MySQL as its backend.

[https://gist.github.com/nathanielove/c51f5c4ee1d79045ffa629237e835157](https://gist.github.com/nathanielove/c51f5c4ee1d79045ffa629237e835157)
You may need to run the following commands to install packages and libraries
```bash
sudo apt-get -y install libmysqlclient-dev
# In virtual environment
python3 -m pip install mysqlclient
```
