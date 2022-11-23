#!/bin/venv python3

import csv
import datetime
import json
import os
import time

import mysql.connector

ROOT = os.path.dirname(os.path.realpath(__file__))

# File path
CONFIG_PATH = os.path.join(ROOT, "config.json")
STUDENTS_TSV_PATH = os.path.join(ROOT, "students.tsv")

# Read MySQL username, password, schema from configuration file
with open(CONFIG_PATH, "r") as f:
    jobj = json.load(f)
    MYSQL_USER = jobj["mysql_user"]
    MYSQL_PWD = jobj["mysql_pwd"]
    MYSQL_DB = jobj["mysql_db"]
    BATCH_SIZE = int(jobj.get("batch_size", 1))
    INDEX_AFTER = jobj.get("index_after_load", False)

assert MYSQL_USER
assert MYSQL_PWD
assert MYSQL_DB

# Open connection to MySQL
conn = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PWD,
                               host="localhost",
                               database=MYSQL_DB)

# Create/Recreate students table
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS students;")
cursor.execute(
    "CREATE TABLE students ("
    "sid BIGINT PRIMARY KEY,"  # Student ID
    "sex TINYINT,"  # Sex, 0 for female, 1 for male
    "lname VARCHAR(64),"  # Last name
    "llname VARCHAR(64),"  # Last name in lower case for indexing purpose
    "fname VARCHAR(64),"  # First name
    "lfname VARCHAR(64),"  # First name in lower case for indexing purpose
    "dob DATE,"  # Date of birth
    "gpa DECIMAL(3,2)"  # GPA as x.yz
    ");")


def create_indexes():
    for col in ("sex", "llname", "lfname", "dob", "gpa"):
        cursor.execute(
            f"CREATE INDEX idx_{col} ON students ({col}) USING BTREE;")
    conn.commit()


# Create indexes before inserting any data
if not INDEX_AFTER:
    create_indexes()

insert_stmt = "INSERT INTO students (sid,sex,lname,llname,fname,lfname," \
              "dob,gpa) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"


def row_to_vals(row: dict) -> tuple:
    return (int(row["sid"]),  # sid
            int(row["sex"]),  # sex
            row["lname"], row["llname"],  # last name
            row["fname"], row["lfname"],  # first name
            datetime.datetime.strptime(row["dob"], "%Y-%m-%d"),  # dob
            float(row["gpa"]))  # gpa


start_time = time.time()
with open(STUDENTS_TSV_PATH, "r") as f:
    csv_rdr = csv.DictReader(f, delimiter="\t")
    if BATCH_SIZE == 1:
        for row in csv_rdr:
            cursor.execute(insert_stmt, row_to_vals(row))
    else:
        batch = []
        for row in csv_rdr:
            batch.append(row_to_vals(row))
            if len(batch) == BATCH_SIZE:
                cursor.executemany(insert_stmt, batch)
                batch.clear()
        if len(batch) > 0:
            cursor.executemany(insert_stmt, batch)
            batch.clear()
conn.commit()

# Create indexes after loading the data
if INDEX_AFTER:
    create_indexes()

end_time = time.time()
print(f"Total time: {end_time - start_time} s")

# Try some queries to see if data has been loaded successfully

# Check number of females/males
cursor.execute("SELECT sex, COUNT(sid) FROM students GROUP BY sex;")
for row in cursor.fetchall():
    if int(row[0]) == 0:
        print(f"Females: {row[1]}")
    else:
        print(f"Males: {row[1]}")

# Print average age
cursor.execute(
    "SELECT AVG(TIMESTAMPDIFF(YEAR, dob, CURDATE())) AS age FROM students;")
res = cursor.fetchone()
print(f"Average age: {round(float(res[0]))}")

# Print min/max/avg GPA
cursor.execute("SELECT MIN(gpa), MAX(gpa), AVG(gpa) FROM students;")
res = cursor.fetchone()
print(f"Min GPA: {res[0]}")
print(f"Max GPA: {res[1]}")
print(f"Avg GPA: {res[2]:.2f}")

cursor.close()
conn.close()
