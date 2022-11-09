## Install Django
Install libraries and packages
```bash
# In virtual environment
python3 -m pip install django
```

Follow the following link to create your first project, don't start the server yet.
[https://docs.djangoproject.com/en/3.2/intro/tutorial01/](https://docs.djangoproject.com/en/3.2/intro/tutorial01/)

Edit */home/ubuntu/mysite/mysite/settings.py*, add your EC2 hostname and IP to `ALLOWED_HOSTS`.

You can test your connection with MySQL with the following script for `polls/views.py`
```python
from django.http import HttpResponse
import mysql.connector

def index(request):
    db_connection = mysql.connector.connect(user="your_name", password="some_password")
    db_cursor = db_connection.cursor()
    db_cursor.execute("USE cs179g;")
    db_cursor.execute("SELECT * FROM Wines LIMIT 5;")
    return HttpResponse(str(db_cursor.fetchall()))
```

After you created / edit the 2 `urls.py` files, add your host name and IP to `mysite/settings.py`, line 28 `ALLOWED_HOSTS`, like
```
ALLOWED_HOSTS = [
	'your_ec2_hostname',
	'your_ec2_ip_address'
]
```
where, `your_ec2_hostmane = cs179g-fall-2022-0#.cs.ucr.edu` (replace `#` with your group number) and `your_ec2_ip_address` is the ip address. To find the ip
address, in the terminal execute:
```bash
ping cs179g-fall-2022-0#.cs.ucr.edu
```
The value that you will see will be your ip address.
Then, migrate
```bash
python3 manage.py migrate
```

Start your website
```bash
# 0.0.0.0:8080 makes your webpage available for public access (from your own machine)
python3 manage.py runserver 0.0.0.0:8080
```

Then visit [http://cs179g-fall-2022-0#.cs.ucr.edu:8080/polls](http://cs179g-fall-2022-0#.cs.ucr.edu:8080/polls/) (Replace # with your group number)
