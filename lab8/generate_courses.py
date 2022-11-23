#!/bin/venv python3

import json
import os
import random
import sys
import uuid
from subprocess import call

from numpy.random import default_rng

ROOT = os.path.dirname(os.path.realpath(__file__))

# File path
CONFIG_PATH = os.path.join(ROOT, "config.json")
COURSES_CSV_PATH = os.path.join(ROOT, "courses.csv")

# Read number of female/male students from configuration
with open(CONFIG_PATH, "r") as f:
    jobj = json.load(f)
    NUM_FEMALES = int(jobj.get("num_females", 10000))
    NUM_MALES = int(jobj.get("num_males", 10000))
    # Perhaps 4 courses in one term
    MIN_COURSES = int(jobj.get("min_courses", 4))
    # Perhaps 6 courses per term, 2 terms per year, 4 years total
    MAX_COURSES = int(jobj.get("max_courses", 48))

MAX_SID = NUM_FEMALES + NUM_MALES
# https://www.pdx.edu/registration/calculating-grade-point-average
GPAS = [0.00, 0.67, 1.00, 1.33, 1.67, 2.00, 2.33, 2.67, 3.00, 3.33, 3.67, 4.00]
# https://www.hilbert.edu/docs/default-source/Academics/Institutional-Research-Assessment/oira_report-on-grade-distributions_2009_12.pdf?sfvrsn=8e29bc3f_0
weights = [5.8, 1.49, 1.49, 4.32, 4.32, 4.32, 10.36, 10.36, 10.36, 15.23, 15.23,
           15.23]

tmp1_path = os.path.join(ROOT, "tmp1")
tmp2_path = os.path.join(ROOT, "tmp2")

total_rows = 0
with open(tmp1_path, "w") as outf:
    # For each student (ID)
    for sid in range(1, MAX_SID + 1):
        # Random number of courses taken
        num_courses = random.randint(MIN_COURSES, MAX_COURSES)
        points = random.choices(GPAS, weights=weights, k=num_courses)
        for i in range(num_courses):
            # Assuming one unique course of one term of one year is
            # identified by UUID.
            # Student ID, course ID, random course credit hour, random grade
            outf.write(f"{sid},{uuid.uuid4().hex},{random.randint(1, 4)},"
                       f"{points[i]:.2f}\n")
            total_rows += 1

print(f"Generated {total_rows} unique records")

# Now the temp file is sorted by student ID, we want to make it random
# The below function can only run on Linux
if sys.platform == "linux" or sys.platform == "linux2":
    call(f"shuf \"{tmp1_path}\" > \"{tmp2_path}\"", shell=True)
    with open(COURSES_CSV_PATH, "w") as outf, \
            open(tmp2_path, "r") as inf:
        outf.write("sid,cid,credit_hour,grade_point\n")
        for line in inf:
            outf.write(line)
    os.remove(tmp1_path)
    os.remove(tmp2_path)
else:
    print("Please run this script on Linux", file=sys.stderr)
