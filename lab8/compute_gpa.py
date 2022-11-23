#!/bin/venv python3

import glob
import json
import os
import shutil
import time

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum
from pyspark.sql.types import IntegerType

ROOT = os.path.dirname(os.path.realpath(__file__))

# File path
CONFIG_PATH = os.path.join(ROOT, "config.json")
COURSES_CSV_PATH = os.path.join(ROOT, "courses.csv")
NAMES_TSV_PATH = os.path.join(ROOT, "names.tsv")
STUDENTS_TSV_PATH = os.path.join(ROOT, "students.tsv")

# Read Spark master URL from config file
with open(CONFIG_PATH, "r") as f:
    jobj = json.load(f)
    SPARK_MASTER = jobj["spark_master"]

start_time = time.time()

# Create a Spark session
spark = SparkSession.builder \
    .master(SPARK_MASTER) \
    .appName("Compute GPA") \
    .getOrCreate()

# Read the courses CSV file into dataframe
# Columns: Student ID, Unique Course ID, Credit Hour, Grade Point
courses_df = spark.read.csv(COURSES_CSV_PATH, header=True) \
    .withColumn("sid", col("sid").cast(IntegerType()))

# The following functions compute cumulative GPA via dataframe's APIs. You can
# also use MapReduce functions for the same purpose. See
# https://stackoverflow.com/questions/29930110/calculating-the-averages-for-each-key-in-a-pairwise-k-v-rdd-in-spark-with-pyth

# 1. Create a new column quality_point by credit_hour * grade_point
# 2. Group by student ID
# 3. Sum credit_hour as total_ch, sum quality_point as total_qp
grouped_df = courses_df \
    .select("sid", "credit_hour",
            (courses_df["credit_hour"] * courses_df["grade_point"])
            .alias("quality_point")) \
    .groupBy("sid") \
    .agg(sum("credit_hour").alias("total_ch"),
         sum("quality_point").alias("total_qp"))

# Compute cumulative GPA by total_qp / total_ch, name as gpa
gpa_df = grouped_df \
    .select("sid",
            (grouped_df["total_qp"] / grouped_df["total_ch"]).alias("gpa"))

# Read students info file (random first/last name, sex, dob)
names_df = spark.read.csv(NAMES_TSV_PATH, sep="\t", header=True) \
    .withColumn("sid", col("sid").cast(IntegerType()))

# Inner join 2 dataframes on sid, such that every student gets her/his GPA
students_df = names_df.join(gpa_df, names_df.sid == gpa_df.sid, "inner") \
    .drop(gpa_df.sid) \
    .sort(names_df.sid)

# Save into TSV file
spark_out_dir = os.path.join(ROOT, "spark_out")
students_df \
    .repartition(1) \
    .write.csv(spark_out_dir, sep="\t", header=True, mode="overwrite")

# Stop Spark session
spark.stop()

end_time = time.time()

# Remove the Spark output folder and move the output TSV file
for f in glob.glob(os.path.join(spark_out_dir, "*")):
    if f.endswith(".csv"):
        os.rename(f, STUDENTS_TSV_PATH)
        break
shutil.rmtree(spark_out_dir)

print(f"Total running time: {end_time - start_time} s")
