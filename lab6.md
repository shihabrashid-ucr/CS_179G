# CS 179G Lab 6

Change number of workers in Spark.
```python
from time import time
from pyspark import SparkContext
for j in range(1,10):
    sc = SparkContext(master=f'local[{j}]')
    t0 = time()
    for i in range(10):
        sc.parallelize([1,2] * 1000000).reduce(lambda x,y:x+y)
    print(f'{j} executors, time= {time() - t0}')
    sc.stop()
```
The goal of today's lab is to do big data processing with Spark on a weather station dataset. We are given two dataset, one with all the weather stations in the world listed and another with temperature, precipitation recordings.

Download the dataset with `gdown` under `lab6/data`
```bash
gdown https://drive.google.com/uc?id=1RIQDzVHKPBa1ae8L47EUyWTNRDluiqSN
gdown https://drive.google.com/uc?id=1hscgeIPMAFM2tIt_c5AcWFkt2hFQHIXD
```

We want to find those US states where the temperature is stable.
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import UserDefinedFunction
from pyspark.sql.types import StringType,IntegerType
from pyspark.sql.functions import collect_list, split, regexp_replace, col, round,concat,lit,avg
```


```python
spark = SparkSession.builder.master("local[*]").appName('weather-station').getOrCreate()
locations = spark.read.format("csv").options(inferschema='true',header='true').load('data/WeatherStationLocations.csv')
locations.show(5)
```

    Setting default log level to "WARN".
    To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).


    22/11/02 05:52:04 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable


                                                                                    

    +------+-----+------------+----+-----+----+----+-------+--------+--------+
    |  USAF| WBAN|STATION NAME|CTRY|STATE| LAT| LON|ELEV(M)|   BEGIN|     END|
    +------+-----+------------+----+-----+----+----+-------+--------+--------+
    |007005|99999|  CWOS 07005|null| null|null|null|   null|20120127|20120127|
    |007011|99999|  CWOS 07011|null| null|null|null|   null|20111025|20120712|
    |007018|99999|  WXPOD 7018|null| null| 0.0| 0.0| 7018.0|20110309|20130730|
    |007019|99999|  CWOS 07019|null| null|null|null|   null|20130625|20130703|
    |007025|99999|  CWOS 07025|null| null|null|null|   null|20120127|20120127|
    +------+-----+------------+----+-----+----+----+-------+--------+--------+
    only showing top 5 rows
    



```python
locations = locations.filter("CTRY = 'US' and STATE is not null")
locations.createOrReplaceTempView("locations_vw")
locations.show(5)
```

    +------+-----+--------------------+----+-----+------+--------+-------+--------+--------+
    |  USAF| WBAN|        STATION NAME|CTRY|STATE|   LAT|     LON|ELEV(M)|   BEGIN|     END|
    +------+-----+--------------------+----+-----+------+--------+-------+--------+--------+
    |423630|99999|MISSISSIPPI CANYO...|  US|   LA| 28.16|  -89.22|   37.0|20130901|20140403|
    |690014|99999|  C STN  WHITE SANDS|  US|   NM| 32.35|-106.367| 1224.0|    null|    null|
    |690020|93218|JOLON HUNTER LIGG...|  US|   CA|  36.0|-121.233|  317.0|    null|    null|
    |690044|99999|              DUGWAY|  US|   UT|40.183|-112.917| 1330.0|    null|    null|
    |690064|99999|    DUGWAY MOBILE #2|  US|   UT|40.217|-112.967| 1335.0|    null|    null|
    +------+-----+--------------------+----+-----+------+--------+-------+--------+--------+
    only showing top 5 rows
    



```python
recordings = spark.read.text('data/2009.txt')
#Filtering the headers in recordings
recordings_df = recordings.filter("value not like 'STN--%'")
#Replacing multiple spaces with single space so that they can be split easily
recordings_df = recordings_df.withColumn("value", regexp_replace(col("value"), " +", " "))
recordings_df.show(5)
```

    +--------------------+
    |               value|
    +--------------------+
    |008209 99999 2009...|
    |008209 99999 2009...|
    |008209 99999 2009...|
    |008209 99999 2009...|
    |008209 99999 2009...|
    +--------------------+
    only showing top 5 rows
    



```python
#User defined function for calculating precipitation
def calc_prec(prec):
    code = prec[-1]
    if code.isdigit():
        return float(prec)
    else:
        value = float(prec[0:-1])
        if code == 'A':
            value = value*4
        if code == 'C':
            value = value*(4/3)
        elif code == 'B' or code == 'E':
            value = value*2
        return value
```


```python
calc_prec = UserDefinedFunction(calc_prec, StringType())
spark.udf.register("calc_prec", calc_prec) # register(name, function)
```




    <pyspark.sql.udf.UserDefinedFunction at 0x7f680709ec80>




```python
 #Creating a new dataframe with only required columns and ignoring the rest
recordings_t = split(recordings_df['value'], ' ')
recordings_df = recordings_df.withColumn('USAF', recordings_t.getItem(0))
recordings_df = recordings_df.withColumn('WBAN', recordings_t.getItem(1))
recordings_df = recordings_df.withColumn('TEMP', recordings_t.getItem(3))
recordings_df = recordings_df.withColumn('MONTH', recordings_t.getItem(2).substr(5, 2).cast("integer"))
recordings_df = recordings_df.withColumn('PRCP', calc_prec(recordings_t.getItem(19)))
recordings_df.show(5)
```

    [Stage 5:>                                                          (0 + 1) / 1]

    +--------------------+------+-----+----+-----+----+
    |               value|  USAF| WBAN|TEMP|MONTH|PRCP|
    +--------------------+------+-----+----+-----+----+
    |008209 99999 2009...|008209|99999|78.2|    3| 0.0|
    |008209 99999 2009...|008209|99999|67.8|    3| 0.0|
    |008209 99999 2009...|008209|99999|68.1|    3| 0.0|
    |008209 99999 2009...|008209|99999|66.6|    3| 0.0|
    |008209 99999 2009...|008209|99999|66.9|    3| 0.0|
    +--------------------+------+-----+----+-----+----+
    only showing top 5 rows
    


                                                                                    


```python
#Removing unnecessary columns  
recordings_df = recordings_df.drop("value").filter("TEMP is not null").filter("PRCP NOT LIKE '99.99'")
recordings_df.createOrReplaceTempView("recordings_vw")
recordings_df.show(5)
```

    [Stage 6:>                                                          (0 + 1) / 1]

    +------+-----+----+-----+----+
    |  USAF| WBAN|TEMP|MONTH|PRCP|
    +------+-----+----+-----+----+
    |008209|99999|78.2|    3| 0.0|
    |008209|99999|67.8|    3| 0.0|
    |008209|99999|68.1|    3| 0.0|
    |008209|99999|66.6|    3| 0.0|
    |008209|99999|66.9|    3| 0.0|
    +------+-----+----+-----+----+
    only showing top 5 rows
    


                                                                                    


```python
#joining the two tables
joined_df = spark.sql("""Select D1.USAF, D1.CTRY, D1.STATE, D2.MONTH, D2.PRCP, D2.TEMP from locations_vw AS D1 inner join recordings_vw AS D2 ON D1.USAF = D2.USAF""")
joined_df.createOrReplaceTempView("joined_vw")
joined_df.show(5)
```

    [Stage 9:>                                                          (0 + 1) / 1]

    +------+----+-----+-----+----+----+
    |  USAF|CTRY|STATE|MONTH|PRCP|TEMP|
    +------+----+-----+-----+----+----+
    |690090|  US|   FL|    1| 0.0|43.7|
    |690090|  US|   FL|    1| 0.0|45.5|
    |690090|  US|   FL|    1| 0.0|46.8|
    |690090|  US|   FL|    1|0.03|39.5|
    |690090|  US|   FL|    1| 0.0|31.7|
    +------+----+-----+-----+----+----+
    only showing top 5 rows
    


                                                                                    


```python
#Finding the state's average temperature recorded for each month
state_month_df = spark.sql("""Select State, Month, Avg(PRCP) as AVG_PRCP, avg(TEMP) as AVG_TEMP From joined_vw GROUP BY State, Month""")
state_month_df.createOrReplaceTempView("state_month_vw")
state_month_df.show(10)
```

    [Stage 11:=============================>                            (1 + 1) / 2]

    +-----+-----+--------------------+------------------+
    |State|Month|            AVG_PRCP|          AVG_TEMP|
    +-----+-----+--------------------+------------------+
    |   CO|    4| 0.04630747126436789|43.348760775862004|
    |   VA|    2|0.010549661066902437| 40.48373121131742|
    |   UT|    4| 0.03804533630620585| 48.86622073578596|
    |   IA|    2| 0.02316023284313724|28.258409926470595|
    |   NC|    7| 0.07631787554498613| 76.47562425683721|
    |   DE|    7| 0.03790697674418605| 73.85116279069767|
    |   ND|    7| 0.07674285714285711| 66.53257142857142|
    |   HI|    6|0.014160855416085536| 76.82384937238511|
    |   AR|    2| 0.07651637505607897| 46.82032301480475|
    |   NC|    3| 0.07879671150971602| 50.98308776425387|
    +-----+-----+--------------------+------------------+
    only showing top 10 rows
    


                                                                                    


```python
# Find the month which has the highest temperature recorded for each state
max_tmp_month_df = spark.sql("""SELECT t1.AVG_TEMP as MAX_TEMP,  t1.STATE, t1.MONTH as MAX_MONTH FROM state_month_vw as t1 JOIN 
(SELECT MAX(AVG_TEMP) as INNER_MAX, STATE FROM state_month_vw GROUP BY STATE) t2 ON t1.STATE = t2.STATE  AND t1.AVG_TEMP = t2.INNER_MAX""")
max_tmp_month_df.createOrReplaceTempView("max_tmp_month_vw")
max_tmp_month_df.show(7)
```

    [Stage 15:=============================>                            (1 + 1) / 2]

    +-----------------+-----+---------+
    |         MAX_TEMP|STATE|MAX_MONTH|
    +-----------------+-----+---------+
    |73.85116279069767|   DE|        7|
    |66.53257142857142|   ND|        7|
    |76.82384937238511|   HI|        6|
    |79.22971497877509|   AR|        6|
    |            83.73|   PR|        7|
    |67.06397550111353|   PA|        6|
    |73.26509433962268|   VA|        6|
    +-----------------+-----+---------+
    only showing top 7 rows
    


                                                                                    


```python
# Find the month which has the lowest temperature recorded for each state
min_tmp_month_df = spark.sql("""SELECT t1.AVG_TEMP as MIN_TEMP,  t1.STATE, t1.MONTH as MIN_MONTH FROM state_month_vw as t1 JOIN 
(SELECT MIN(AVG_TEMP) as INNER_MIN, STATE FROM state_month_vw GROUP BY STATE) t2 ON t1.STATE = t2.STATE  AND t1.AVG_TEMP = t2.INNER_MIN""")
min_tmp_month_df.createOrReplaceTempView("min_tmp_month_vw")
min_tmp_month_df.show(7)
```

    [Stage 24:=============================>                            (1 + 1) / 2]

    +------------------+-----+---------+
    |          MIN_TEMP|STATE|MIN_MONTH|
    +------------------+-----+---------+
    | 36.11773913043478|   TN|        1|
    |24.281004366812205|   WY|        1|
    | 48.66211859527918|   AZ|        1|
    | 49.58779465688838|   TX|        1|
    |27.081522956326978|   NJ|        1|
    | 39.95071315372428|   NV|        1|
    |24.460432766615142|   CT|        1|
    +------------------+-----+---------+
    only showing top 7 rows

```python
# Join the max month table and min month table
max_min_df = spark.sql("""Select max_tmp_month_vw.STATE, max_tmp_month_vw.MAX_TEMP, max_tmp_month_vw.MAX_MONTH, min_tmp_month_vw.MIN_TEMP, min_tmp_month_vw.MIN_MONTH FROM max_tmp_month_vw JOIN 
min_tmp_month_vw ON max_tmp_month_vw.STATE = min_tmp_month_vw.STATE""")
max_min_df.createOrReplaceTempView('max_min_vw')
max_min_df.show(7)
```

                                                                                    

    +-----+-----------------+---------+------------------+---------+
    |STATE|         MAX_TEMP|MAX_MONTH|          MIN_TEMP|MIN_MONTH|
    +-----+-----------------+---------+------------------+---------+
    |   AZ|85.55714285714288|        7| 48.66211859527918|        1|
    |   SC|79.39328358208952|        7|43.868591065292065|        1|
    |   LA| 84.9547520661157|        7|52.287098560354245|        1|
    |   MN|65.62787934186473|        7|3.9970097357440926|        1|
    |   NJ|70.87811158798281|        7|27.081522956326978|        1|
    |   DC|74.97500000000001|        7|32.229032258064514|        1|
    |   OR|65.15714285714284|        7|37.184996651038176|        1|
    +-----+-----------------+---------+------------------+---------+
    only showing top 7 rows
    



```python
# coalesce decreases the number of partitions
difference_df = spark.sql("""Select *, MAX_TEMP-MIN_TEMP as DIFFERENCE FROM max_min_vw WHERE (MAX_TEMP <> 0 AND MIN_TEMP <> 0) ORDER BY DIFFERENCE ASC """)
difference_df.show(7)
difference_df.coalesce(1).write.option("header", "true").option("delimiter", ",").mode("overwrite").csv("data/output")
```

                                                                                    

    +-----+-----------------+---------+------------------+---------+------------------+
    |STATE|         MAX_TEMP|MAX_MONTH|          MIN_TEMP|MIN_MONTH|        DIFFERENCE|
    +-----+-----------------+---------+------------------+---------+------------------+
    |   VI|83.50000000000001|        7|   75.858064516129|        3| 7.641935483871009|
    |   HI|76.82384937238511|        6| 68.49798136645961|        2|   8.3258680059255|
    |   PR|            83.73|        7| 74.89545454545454|        2| 8.834545454545463|
    |   CA|69.66763142350858|        7| 50.60731882754901|        2|19.060312595959573|
    |   FL|82.42849109653233|        7| 59.01381704980827|        1| 23.41467404672406|
    |   OR|65.15714285714284|        7|37.184996651038176|        1|27.972146206104668|
    |   WA|65.99965811965816|        7|35.362190650779105|        1| 30.63746746887906|
    +-----+-----------------+---------+------------------+---------+------------------+
    only showing top 7 rows
    


                                                                                    


```python
def convert_month(m):
    dict = {1 : 'JAN', 2 : 'FEB', 3 : 'MAR', 4 : 'APR', 5 : 'MAY',
            6 : 'JUN', 7 : 'JUL', 8 : 'AUG', 9 : 'SEPT', 10 : 'OCT',
            11 : 'NOV', 12 : 'DEC'}
    return dict[m]
conv_month = UserDefinedFunction(lambda x : convert_month(x), StringType())
spark.udf.register("convert_month", conv_month)
difference_df = difference_df.withColumn('MAX_MONTH', conv_month('MAX_MONTH'))
difference_df = difference_df.withColumn('MIN_MONTH', conv_month('MIN_MONTH'))
difference_df.show(5)
```

    22/11/02 06:45:25 WARN SimpleFunctionRegistry: The function convert_month replaced a previously registered function.


                                                                                    

    +-----+-----------------+---------+-----------------+---------+------------------+
    |STATE|         MAX_TEMP|MAX_MONTH|         MIN_TEMP|MIN_MONTH|        DIFFERENCE|
    +-----+-----------------+---------+-----------------+---------+------------------+
    |   VI|83.50000000000001|      JUL|  75.858064516129|        3| 7.641935483871009|
    |   HI|76.82384937238511|      JUN|68.49798136645961|        2|   8.3258680059255|
    |   PR|            83.73|      JUL|74.89545454545454|        2| 8.834545454545463|
    |   CA|69.66763142350858|      JUL|50.60731882754901|        2|19.060312595959573|
    |   FL|82.42849109653233|      JUL|59.01381704980827|        1| 23.41467404672406|
    +-----+-----------------+---------+-----------------+---------+------------------+
    only showing top 5 rows
    



```python
difference_df.coalesce(1).write.option("header", "true").option("delimiter", ",").mode("overwrite").csv("data/output")
```

                                                                                    


```python
difference_df.show(7)
```

                                                                                    

    +-----+-----------------+---------+------------------+---------+------------------+
    |STATE|         MAX_TEMP|MAX_MONTH|          MIN_TEMP|MIN_MONTH|        DIFFERENCE|
    +-----+-----------------+---------+------------------+---------+------------------+
    |   VI|83.50000000000001|      JUL|   75.858064516129|      MAR| 7.641935483871009|
    |   HI|76.82384937238511|      JUN| 68.49798136645961|      FEB|   8.3258680059255|
    |   PR|            83.73|      JUL| 74.89545454545454|      FEB| 8.834545454545463|
    |   CA|69.66763142350858|      JUL| 50.60731882754901|      FEB|19.060312595959573|
    |   FL|82.42849109653233|      JUL| 59.01381704980827|      JAN| 23.41467404672406|
    |   OR|65.15714285714284|      JUL|37.184996651038176|      JAN|27.972146206104668|
    |   WA|65.99965811965816|      JUL|35.362190650779105|      JAN| 30.63746746887906|
    +-----+-----------------+---------+------------------+---------+------------------+
    only showing top 7 rows
    
# Task:
1. Create a User defined function in Spark to convert the month value to String, i.e. 1 = JAN, 2 = FEB etc. Update the dataframe to reflect this
2. Rank the US states by their stable-ness. Order the states in an ascending order by the difference between `MAX_TEMP` and `MIN_TEMP`
                                              
