import json
import os

import mysql.connector
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# File path
CONFIG_PATH = os.path.join(ROOT, "config.json")

# Read MySQL username, password, database from configuration file
with open(CONFIG_PATH, "r") as f:
    jobj = json.load(f)
    MYSQL_USER = jobj["mysql_user"]
    MYSQL_PWD = jobj["mysql_pwd"]
    MYSQL_DB = jobj["mysql_db"]


@csrf_exempt
def index(request):
    return render(request, "index.html")


@csrf_exempt
def search(request):
    print(request.method)
    if request.method != "POST":
        return HttpResponse("Invalid request!")

    params = request.POST

    fields = []
    values = []
    # First and last indexed name
    if params.get("fname", ""):
        fields.append("lfname = %s")
        values.append(params["fname"].lower())
    if params.get("lname", ""):
        fields.append("llname = %s")
        values.append(params["lname"].lower())
    # Sex
    sex = params.get("sex", "")
    if sex == "f":
        fields.append("sex = %s")
        values.append(0)
    elif sex == "m":
        fields.append("sex = %s")
        values.append(1)
    # GPA
    if params.get("min_gpa", ""):
        fields.append("gpa >= %s")
        values.append(float(params["min_gpa"]))
    if params.get("max_gpa", ""):
        fields.append("gpa <= %s")
        values.append(float(params["max_gpa"]))
    # ORDER_BY clause
    arg_order = params.get("order", "lname")
    if arg_order == "fname":
        order_by = "lfname"
    elif arg_order == "age":
        order_by = "age"
    elif arg_order == "gpa":
        order_by = "gpa"
    else:
        order_by = "llname"
    asc = "DESC" if params.get("asc", "0") == "0" else "ASC"

    limit_no = int(params.get("limit", 20))

    # SQL query template
    query = f"SELECT fname, lname, sex, TIMESTAMPDIFF(YEAR, dob, CURDATE(" \
            f")) as age, gpa FROM students"
    if fields:
        query += " WHERE " + " AND ".join(fields)
    query += f" ORDER BY {order_by} {asc} LIMIT {limit_no};"
    print(query)
    # Open connection to MySQL
    conn = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PWD,
                                   host="localhost",
                                   database=MYSQL_DB)
    cursor = conn.cursor()
    # Execute the SELECT query
    cursor.execute(query, values)

    # HTML content
    lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<style>",
        "table, th, td {",
        "  border:1px solid black;",
        "}",
        "</style>",
        "<body>",
        "<table>",
        "  <tr>",
        "    <th>#</th>",
        "    <th>First Name</th>",
        "    <th>Last Name</th>",
        "    <th>Sex</th>",
        "    <th>Age</th>",
        "    <th>GPA</th>",
        "  </tr>",
    ]
    num = 1
    for row in cursor.fetchall():
        lines.append("  <tr>")
        # Result number
        lines.append(f"    <th>{num}</th>")
        num += 1
        # First name
        lines.append(f"    <th>{row[0]}</th>")
        # Last name
        lines.append(f"    <th>{row[1]}</th>")
        # Sex, F or M
        if int(row[2]) == 0:
            lines.append("    <th>F</th>")
        else:
            lines.append("    <th>M</th>")
        # Age
        lines.append(f"    <th>{int(row[3])}</th>")
        # GPA
        lines.append(f"    <th>{float(row[4]):.2f}</th>")
        lines.append("  </tr>")
    lines.append("</table>")
    lines.append("</body>")
    lines.append("</html>")
    cursor.close()
    conn.close()
    return HttpResponse("\n".join(lines))
