#!/bin/venv python3

import csv
import datetime
import json
import os
import random
import urllib.request

FEMALE_NAMES_URL = "https://raw.githubusercontent.com/datasets-io/female" \
                   "-first-names-en/master/lib/dataset.json"
MALE_NAMES_URL = "https://raw.githubusercontent.com/datasets-io/male-first" \
                 "-names-en/master/lib/dataset.json"
SURNAMES_URL = "https://raw.githubusercontent.com/fivethirtyeight/data/master" \
               "/most-common-name/surnames.csv"

ROOT = os.path.dirname(os.path.realpath(__file__))

# File path
CONFIG_PATH = os.path.join(ROOT, "config.json")
NAMES_TSV_PATH = os.path.join(ROOT, "names.tsv")

# Read number of female/male students from configuration
with open(CONFIG_PATH, "r") as f:
    jobj = json.load(f)
    NUM_FEMALES = int(jobj.get("num_females", 10000))
    NUM_MALES = int(jobj.get("num_males", 10000))


def get_firstnames(url: str) -> list:
    with urllib.request.urlopen(url) as req:
        jobj = json.loads(req.read())
        return list(jobj)


# Lists of female/male first names
female_firstnames = get_firstnames(FEMALE_NAMES_URL)
male_firstnames = get_firstnames(MALE_NAMES_URL)

# Get lastnames
lastnames = []
chunk_size = 1024 ** 2  # 1 MB
lasname_path = os.path.join(ROOT, "lastnames.csv")
if not os.path.isfile(lasname_path):
    with urllib.request.urlopen(SURNAMES_URL) as req, \
            open(lasname_path, "bw") as outf:
        # Download chunk by chunk to avoid out-of-memory
        buf = req.read(chunk_size)
        while buf:
            outf.write(buf)
            buf = req.read(chunk_size)

# Extract the last name from the raw CSV file and capitalize each last name
with open(lasname_path, "r") as f:
    csv_rdr = csv.reader(f, delimiter=",")
    next(csv_rdr)  # Skip header row
    for row in csv_rdr:
        lastname = row[0].capitalize()
        lastnames.append(lastname)

# Used to generate random date of birth between 1970-1-1 to 2003-12-31
start_date = datetime.date(1970, 1, 1)
end_date = datetime.date(2003, 12, 31)
time_between_dates = end_date - start_date
days_between_dates = time_between_dates.days


def random_dob() -> str:
    r_days = random.randrange(days_between_dates)
    r_date = start_date + datetime.timedelta(days=r_days)
    return r_date.strftime("%Y-%m-%d")


def random_gpa() -> str:
    return "{:.2f}".format(random.uniform(2.0, 4.0))


with open(NAMES_TSV_PATH, "w") as outf:
    cols = ["sid", "sex", "lname", "llname", "fname", "lfname", "dob"]
    csv_wtr = csv.DictWriter(outf, fieldnames=cols, delimiter="\t")
    csv_wtr.writeheader()
    female_remains = NUM_FEMALES
    male_remains = NUM_MALES
    for sid in range(1, NUM_FEMALES + NUM_MALES + 1):
        # Random lastname
        r_lastname = random.choice(lastnames)
        if female_remains > 0 and male_remains > 0:
            # Have not yet generated all the females and males
            is_female = random.randint(0, 1) == 0
        elif female_remains > 0:
            # Have already generated all the males
            is_female = True
        else:
            # Have already generated all the females
            is_female = False
        if is_female:
            r_firstname = random.choice(female_firstnames)
            sex = 0  # 0 for female
            female_remains -= 1
        else:
            r_firstname = random.choice(male_firstnames)
            sex = 1  # 1 for male
            male_remains -= 1
        # Lower case letter for case insensitive search
        csv_wtr.writerow({
            "sid": sid,
            "sex": sex,
            "lname": r_lastname,
            "llname": r_lastname.lower(),
            "fname": r_firstname,
            "lfname": r_firstname.lower(),
            "dob": random_dob(),
        })
