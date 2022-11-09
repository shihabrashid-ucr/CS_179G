## Install Django
Install libraries and packages
```bash
# In virtual environment
python3 -m pip install django
```

Reference: [https://docs.djangoproject.com/en/3.2/intro/tutorial01/](https://docs.djangoproject.com/en/3.2/intro/tutorial01/)

Create a new folder called `lab7` and `cd` into it.
## Running a basic Django web server

Start your Django project by:
```bash
django-admin startproject mysite
```
This will create your project directory. Inside one project directory there can be multiple `apps`.
This is how the project structure looks:
```
mysite/
    manage.py
    mysite/
        __init__.py
        settings.py
        urls.py
        asgi.py
        wsgi.py
```
(See the reference website for more details on these files)

### Creating a polls app:
```bash
python3 manage.py startapp polls
```
Edit */home/ubuntu/lab7/mysite/mysite/settings.py*, add your EC2 hostname and IP to `ALLOWED_HOSTS`, line 28.
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

Let’s write the first view. Open the file `polls/views.py` and put the following Python code in it:
```python
from django.http import HttpResponse
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
```

This is the simplest view possible in Django. To call the view, we need to map it to a URL - and for this we need a URLconf.
To create a URLconf in the polls directory, create a file called `urls.py`. Your app directory should now look like:
In the `polls/urls.py` file include the following code:
```python
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
]
```
The next step is to point the root URLconf at the polls.urls module. In `mysite/urls.py`, add an import for django.urls.include and insert an include() in the urlpatterns list, so you have:
```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
```
Migrate
```bash
python3 manage.py migrate
```

Start your website
```bash
# 0.0.0.0:8080 makes your webpage available for public access (from your own machine)
python3 manage.py runserver 0.0.0.0:8080
```
Then visit [http://cs179g-fall-2022-0#.cs.ucr.edu:8080/polls](http://cs179g-fall-2022-0#.cs.ucr.edu:8080/polls/) (Replace # with your group number)

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
To render a HTML, edit the `mysite/settings.py` `INSTALLED_APPS`:
```
INSTALLED_APPS = [
    'polls.apps.PollsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```
Create a `templates` directory under `polls` folder. Inside `templates` create a HTML file called `index.html`.
<!DOCTYPE html>
<html lang="en">
   <head></head>
   <body>
      <h1>This is a demo app</h1>
   </body>
</html>
edit the `polls/views.py` The return statement should be something like:
```python3
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import mysql.connector

def index(request):
    return render(request, 'index.html')
```
run `python3 manage.py migrate` again before running the webserver.
