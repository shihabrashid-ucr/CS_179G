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

Download the dataset with `gdown`
```bash
gdown https://drive.google.com/uc?id=1RIQDzVHKPBa1ae8L47EUyWTNRDluiqSN
gdown https://drive.google.com/uc?id=1hscgeIPMAFM2tIt_c5AcWFkt2hFQHIXD
```
