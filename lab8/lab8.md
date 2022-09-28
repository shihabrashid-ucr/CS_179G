# CS 179G Lab 8

Example project.

## Part 1: Data generation (simulation of crawling)
Here I will randomly generate some data as the examples.

Suppose we have two datasets, one dataset is some basic information of students, like student ID, sex, first/last name, date of birth. The other is a dataset of all the grades that all students have received in all courses.

### Names dataset
This is students' information with the following columns:
1. `sid`: Unique student ID, integer type
2. `sex`: Sex, 0 for female, 1 for male. We can store it as `SMALLINT` in MySQL
3. `lname`:  (Capitalized) last name
4. `fname`: (Capitalized) first name
5. `dob`: Date of birth, in the format of `yyyy-mm-dd`

There are also 2 alternative columns which will be used for indexing purpose.
- `llname`: Lower case last name.
- `lfname`: Lower case first name.

If you want to show the actual name to the users, you will need to use `lname` and `fname`. However, if the user just searches by a name in any letter case, you will need to do an expensive case insensitive search in the database. To make this search faster, we can have 2 columns holding names in lower case. To search, we will first convert the searched key into lower case, then do an exact match query or range query to find the names.

For example, the user can enter `Tom`, `tom`, `TOM`, `tOm`, all will be converted to `tom` before passing to the database. The database can find any records that equal to `tom`, and return the actual name `Tom` to the user.

#### Names dataset generation
1. Edit **config.json** to modify the number of female `num_females` and male  `num_males` students to generate. The default value of both is 10000.
2. Run `python3 genereate_names.py`, the output file is saved as **names.tsv**

### Courses dataset
This is a collection of all grades that all students have received. One unique record can be identified as <*student_id*, *course_code*, *year*, *term*>. Here student ID will be the same as `sid` in the names dataset, the triplet <*course_code*, *year*, *term*> is represented by UUID (128 bit integer, 32 bytes hex-decimal string) for simplicity, since these three columns will not be actually used. The dataset contains the following columns:
1. `sid`
2. `cid`: Unique course ID, representing <*course_code*, *year*, *term*>
3. `credit_hour`: Credit hour of the course, from 1 to 4
4. `grade_point`: The grade the student received. Values come from [here](https://www.pdx.edu/registration/calculating-grade-point-average)

#### Courses dataset generation
1. Edit **config.json** to modify `min_courses` (default 4) and `max_courses` (default 48). The total number of courses a students had taken will be randomly generated between these 2 values.
2. Run `python3 genereate_courses.py`, the output file is saved as **courses.csv**

## Part 2: Data processing
Suppose we want to compute the cumulative GPA of all students and save the values into the database. How cumulative GPA is computed can be found at [here](https://www.pdx.edu/registration/calculating-grade-point-average). Generally, the GPA is computed as `sum([credit_hour * grade_point for credit_hour, grade_point in courses) / sum(credit_hour)` for each student. So here we need 4 steps:
1. Compute `credit_hour * grade_point` for each unique course
2. Group by `sid` so we can compute `credit_hour` and `grade_point` for each student.
3. Compute the two sums
4. Make the division to get cumulative GPAs

The above 4 steps can be replaced by a set of MapReduce functions, see [this page](https://stackoverflow.com/questions/29930110/calculating-the-averages-for-each-key-in-a-pairwise-k-v-rdd-in-spark-with-pyth) for more information.

After the above 4 steps, we already have the unique mapping of `sid` to `gpa`. Next, we need to combine this information with the students' name information, by using `join`. Once it's done, we are ready to write the data into the database. Note here, we don't need to directly write the data into the database, this may be less efficient than creating some temporary file and  using batch insertion to load to the database.

### Compute cumulative GPA and join with students' names
1. Edit **config.json** to modify `spark_master` to test with local/cluster mode with different number of cores/workers
2. Run `spark-submit compute_gpa.py`. Results are saved to **students.tsv**

### Load data into MySQL
1. Edit **config.json** to modify `mysql_user`, `mysql_pwd` and `mysql_db` to your own MySQL credentials.  You may change `batch_size` and `index_after_load` to see if there is any performance changes. If `batch_size`  == 1, the script will insert records to MySQL one by one. If `batch_size` > 1, the script will insert multiple records in one query to MySQL. 
2. Run `python3 sql_insertion.py`. The script also contains some test queries to check if insertions were successful.

## Part 3: Web interface
Suppose we just want to build a simple search engine that can show different results based on certain user selected filtering conditions, such as name, sex, gpa range.

1. In virtual environment, run the following command to create a Django project
	```bash
	django-admin startproject demo
	```

2. Add your hostname and IP address to `ALLOWED_HOSTS` in **demo/demo/settings.py**, you should have something like
	```python
	ALLOWED_HOSTS = [
	    'cs179g-fall-2021-06.cs.ucr.edu',
	    '3.131.35.238'
	]
	```
	You can find your IP address by `ping` it. For example, `ping cs179g-fall-2021-06.cs.ucr.edu`, you will get *3.131.35.238*

3. Create an app for the home page
	```bash
	cd demo
	python3 manage.py startapp home
	```
4. Add `'home.apps.HomeConfig'` to `INSTALLED_APPS` in **demo/demo/settings.py**, you should have something like
	```python
	INSTALLED_APPS = [
	    'django.contrib.admin',
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.messages',
	    'django.contrib.staticfiles',
	    'home.apps.HomeConfig',
	]
	```
5. Modify **demo/demo/urls.py** like below
	```python
	from django.contrib import admin
	from django.urls import path
	from django.views.generic import RedirectView
	from django.conf.urls.static import static
	from django.conf.urls import include
	from django.conf import settings

	urlpatterns = [
	    path('admin/', admin.site.urls),
	    path('home/', include('home.urls')),
	    path('', RedirectView.as_view(url='home/', permanent=True)),
	] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	```

6. Create file **urls.py** under **demo/home/** with the following content
	```python
	from django.urls import path
	from . import views

	urlpatterns = [
	    path('', views.index, name='index'),
        path('search', views.search, name='search'),
	]
	```

7. Create folder **templates** under **demo/home/**, and file **index.html** under **templates**. You can write your own HTML code there.

8. Check the two functions in **demo/home/views.py** for rendering a webpage and handling request.

9. Migrate
	```bash
	python3 manage.py migrate
	``` 

10.  Start web service
		```bash
		python3 manage.py runserver 0.0.0.0:8080
		```

11. You can access your web interface at [http://cs179g-fall-2021-0#.cs.ucr.edu:8080](http://cs179g-fall-2021-0#.cs.ucr.edu:8080), modify the hostname to your instance.