# CS 179G Lab 5

# PySpark with Machine Learning - Twitter Sentiment Analysis

Ref: https://www.kaggle.com/code/diniftikhar025/sentimentanalysiswithlogisticregressioninpyspark/notebook
### 1. Download Twitter sentiment analysis training data
```bash
gdown https://drive.google.com/uc?id=1zSkudfJkgL_NChvK2EqzU50sGpB375Aq
```
Install NLTK
```bash
pip3 install nltk
```

The twitter data has following properties:
```
target: the polarity of the tweet (0 = negative, 2 = neutral, 4 = positive)
ids: The id of the tweet ( 2087)
date: the date of the tweet (Sat May 16 23:58:44 UTC 2009)
flag: The query (lyx). If there is no query, then this value is NO_QUERY.
user: the user that tweeted (robotickilldozr)
text: the text of the tweet (Lyx is cool)
```

### 2. Run the following code
```python
import pyspark
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyspark.sql import functions as func
from pyspark.sql.types import StringType,FloatType
import nltk
from pyspark.sql import SparkSession
```

### Reading the data


```python
spark = SparkSession.builder.master('local[*]').appName('Twitter').getOrCreate()
df = spark.read.csv("data/twitter_sentiment_train.csv", inferSchema=True)
```

                                                                                    




    Row(_c0=0, _c1=1467810369, _c2='Mon Apr 06 22:19:45 PDT 2009', _c3='NO_QUERY', _c4='_TheSpecialOne_', _c5="@switchfoot http://twitpic.com/2y1zl - Awww, that's a bummer.  You shoulda got David Carr of Third Day to do it. ;D")




```python
df.show(5)
```

    +------+----------+--------------------+--------+---------------+--------------------+
    |target|        id|                date|    flag|           user|                text|
    +------+----------+--------------------+--------+---------------+--------------------+
    |     0|1467810369|Mon Apr 06 22:19:...|NO_QUERY|_TheSpecialOne_|@switchfoot http:...|
    |     0|1467810672|Mon Apr 06 22:19:...|NO_QUERY|  scotthamilton|is upset that he ...|
    |     0|1467810917|Mon Apr 06 22:19:...|NO_QUERY|       mattycus|@Kenichan I dived...|
    |     0|1467811184|Mon Apr 06 22:19:...|NO_QUERY|        ElleCTF|my whole body fee...|
    |     0|1467811193|Mon Apr 06 22:19:...|NO_QUERY|         Karoli|@nationwideclass ...|
    +------+----------+--------------------+--------+---------------+--------------------+
    only showing top 5 rows
    


### Renaming a column


```python
df = df.withColumnRenamed('_c0','target').withColumnRenamed('_c1','id').withColumnRenamed('_c2','date')\
  .withColumnRenamed('_c3','flag').withColumnRenamed('_c4','user').withColumnRenamed('_c5','text')
df.show(5)
print(f"There are {df.count()} rows and  {len(df.columns)} columns in the dataset.")
```

    +------+----------+--------------------+--------+---------------+--------------------+
    |target|        id|                date|    flag|           user|                text|
    +------+----------+--------------------+--------+---------------+--------------------+
    |     0|1467810369|Mon Apr 06 22:19:...|NO_QUERY|_TheSpecialOne_|@switchfoot http:...|
    |     0|1467810672|Mon Apr 06 22:19:...|NO_QUERY|  scotthamilton|is upset that he ...|
    |     0|1467810917|Mon Apr 06 22:19:...|NO_QUERY|       mattycus|@Kenichan I dived...|
    |     0|1467811184|Mon Apr 06 22:19:...|NO_QUERY|        ElleCTF|my whole body fee...|
    |     0|1467811193|Mon Apr 06 22:19:...|NO_QUERY|         Karoli|@nationwideclass ...|
    +------+----------+--------------------+--------+---------------+--------------------+
    only showing top 5 rows
    


    [Stage 8:>                                                          (0 + 2) / 2]

    There are 1600000 rows and  6 columns in the dataset.


                                                                                    

### Checking for missing values


```python
df.select([func.count(func.when(func.isnan(c),c)).alias(c) for c in df.columns]).toPandas().head()
# Handle duplicates
df = df.dropDuplicates()
```

                                                                                    




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>target</th>
      <th>id</th>
      <th>date</th>
      <th>flag</th>
      <th>user</th>
      <th>text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



We only need the target and the text column for sentiment analyses, that's why dropping the rest of the columns.


```python
drop_cols= ("id","date","flag","user")
df = df.drop(*drop_cols)
df.show(5, truncate = False)
```

    +------+-------------------------------------------------------------------------------------------------------------------+
    |target|text                                                                                                               |
    +------+-------------------------------------------------------------------------------------------------------------------+
    |0     |@switchfoot http://twitpic.com/2y1zl - Awww, that's a bummer.  You shoulda got David Carr of Third Day to do it. ;D|
    |0     |is upset that he can't update his Facebook by texting it... and might cry as a result  School today also. Blah!    |
    |0     |@Kenichan I dived many times for the ball. Managed to save 50%  The rest go out of bounds                          |
    |0     |my whole body feels itchy and like its on fire                                                                     |
    |0     |@nationwideclass no, it's not behaving at all. i'm mad. why am i here? because I can't see you all over there.     |
    +------+-------------------------------------------------------------------------------------------------------------------+
    only showing top 5 rows
    


The negative label is identified as 0 and positive as 4. Let's change the value of Positive from 4 to 1.


```python
df.createOrReplaceTempView('temp')
df = spark.sql('SELECT CASE target WHEN 4 THEN 1.0  ELSE 0 END AS label, text FROM temp')
df.tail(5)
```

    +-----+-------------------------------------------------------------------------------------------------------------------+
    |label|text                                                                                                               |
    +-----+-------------------------------------------------------------------------------------------------------------------+
    |0.0  |@switchfoot http://twitpic.com/2y1zl - Awww, that's a bummer.  You shoulda got David Carr of Third Day to do it. ;D|
    |0.0  |is upset that he can't update his Facebook by texting it... and might cry as a result  School today also. Blah!    |
    |0.0  |@Kenichan I dived many times for the ball. Managed to save 50%  The rest go out of bounds                          |
    |0.0  |my whole body feels itchy and like its on fire                                                                     |
    |0.0  |@nationwideclass no, it's not behaving at all. i'm mad. why am i here? because I can't see you all over there.     |
    +-----+-------------------------------------------------------------------------------------------------------------------+
    only showing top 5 rows
    


Lets see how many samples there are per class


```python
df.groupBy("label").count().show()
```

    [Stage 17:>                                                         (0 + 2) / 2]

    +-----+------+
    |label| count|
    +-----+------+
    |  0.0|800000|
    |  1.0|800000|
    +-----+------+
    


                                                                                    

### Text Preprocessing


```python
from nltk.corpus import stopwords
from  nltk.stem import SnowballStemmer
import re
```


```python
nltk.download('stopwords')
stop_words = stopwords.words("english")
stemmer = SnowballStemmer("english")
text_cleaning_re = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"
```

    [nltk_data] Downloading package stopwords to /home/ubuntu/nltk_data...
    [nltk_data]   Unzipping corpora/stopwords.zip.



```python
def preprocess(text, stem=False):
    # Remove link,user and special characters
    text = re.sub(text_cleaning_re, ' ', str(text).lower()).strip()
    tokens = []
    for token in text.split():
        if token not in stop_words:
            if stem:
                tokens.append(stemmer.stem(token))
            else:
                tokens.append(token)
    return " ".join(tokens)
```


```python
#Use pysparks function udf (user defined functions) to create our own preprocess function
clean_text = func.udf(lambda x: preprocess(x), StringType())

df = df.withColumn('text_cleaned',clean_text(func.col("text")))
df.show(5)
```

    +-----+--------------------+--------------------+
    |label|                text|        text_cleaned|
    +-----+--------------------+--------------------+
    |  0.0|@switchfoot http:...|awww bummer shoul...|
    |  0.0|is upset that he ...|upset update face...|
    |  0.0|@Kenichan I dived...|dived many times ...|
    |  0.0|my whole body fee...|whole body feels ...|
    |  0.0|@nationwideclass ...|    behaving mad see|
    +-----+--------------------+--------------------+
    only showing top 5 rows
    



```python
df = df.drop("text")
```

### Displaying WordCloud


```python
from wordcloud import WordCloud
```


```python
pandas_df = df.toPandas()
plt.figure(figsize = (20,16)) 
wc = WordCloud(max_words = 800 , width = 1200 , height = 600).generate(" ".join(pandas_df[pandas_df["label"]==1.0].text_cleaned))
plt.imshow(wc , interpolation = 'bilinear')
```

                                                                                    




    <matplotlib.image.AxesImage at 0x7fe074320e20>




    
![png](sentiment-pyspark_files/sentiment-pyspark_22_2.png)
    


### Preparing data for model building


```python
from pyspark.ml.feature import Tokenizer
```


```python
tokenizer = Tokenizer(inputCol="text_cleaned", outputCol="words_tokens")
words_tokens = tokenizer.transform(df)
words_tokens.show(5)
```

    +-----+--------------------+--------------------+
    |label|        text_cleaned|        words_tokens|
    +-----+--------------------+--------------------+
    |  0.0|awww bummer shoul...|[awww, bummer, sh...|
    |  0.0|upset update face...|[upset, update, f...|
    |  0.0|dived many times ...|[dived, many, tim...|
    |  0.0|whole body feels ...|[whole, body, fee...|
    |  0.0|    behaving mad see|[behaving, mad, see]|
    +-----+--------------------+--------------------+
    only showing top 5 rows
    


                                                                                    

Applying CounteVectorizer


```python
from pyspark.ml.feature import CountVectorizer
```


```python
count = CountVectorizer (inputCol="words_tokens", outputCol="rawFeatures")
model = count.fit(words_tokens)
featurizedData = model.transform(words_tokens)
featurizedData.show(5)
```

                                                                                    

    22/10/26 23:40:59 WARN DAGScheduler: Broadcasting large task binary with size 2.8 MiB
    +-----+--------------------+--------------------+--------------------+
    |label|        text_cleaned|        words_tokens|         rawFeatures|
    +-----+--------------------+--------------------+--------------------+
    |  0.0|awww bummer shoul...|[awww, bummer, sh...|(262144,[1,10,341...|
    |  0.0|upset update face...|[upset, update, f...|(262144,[6,67,169...|
    |  0.0|dived many times ...|[dived, many, tim...|(262144,[4,209,24...|
    |  0.0|whole body feels ...|[whole, body, fee...|(262144,[3,323,37...|
    |  0.0|    behaving mad see|[behaving, mad, see]|(262144,[20,482,1...|
    +-----+--------------------+--------------------+--------------------+
    only showing top 5 rows
    


                                                                                    

Applying TF-IDF


```python
from pyspark.ml.feature import IDF
```


```python
idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

rescaledData.select("label", "features").show(5) 
```

    22/10/26 23:42:22 WARN DAGScheduler: Broadcasting large task binary with size 2.8 MiB


                                                                                    

    22/10/26 23:43:11 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB
    +-----+--------------------+
    |label|            features|
    +-----+--------------------+
    |  0.0|(262144,[1,10,341...|
    |  0.0|(262144,[6,67,169...|
    |  0.0|(262144,[4,209,24...|
    |  0.0|(262144,[3,323,37...|
    |  0.0|(262144,[20,482,1...|
    +-----+--------------------+
    only showing top 5 rows
    


We only want the `label` and `features` column of the data


```python
df_final = rescaledData.select("label", "features")
```

Splitting the data into `train` and `test` sets


```python
seed = 42  # set seed for reproducibility
trainDF, testDF = df_final.randomSplit([0.7,0.3],seed)
```


```python
trainDF.groupby("label").count().show() # to see if there is any bias
```

    22/10/26 23:48:22 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB


    [Stage 32:>                                                         (0 + 2) / 2]

    22/10/26 23:49:00 WARN RowBasedKeyValueBatch: Calling spill() on RowBasedKeyValueBatch. Will not spill but return 0.
    22/10/26 23:49:00 WARN RowBasedKeyValueBatch: Calling spill() on RowBasedKeyValueBatch. Will not spill but return 0.
    22/10/26 23:49:01 WARN RowBasedKeyValueBatch: Calling spill() on RowBasedKeyValueBatch. Will not spill but return 0.
    22/10/26 23:49:03 WARN RowBasedKeyValueBatch: Calling spill() on RowBasedKeyValueBatch. Will not spill but return 0.
    22/10/26 23:49:04 WARN RowBasedKeyValueBatch: Calling spill() on RowBasedKeyValueBatch. Will not spill but return 0.
    22/10/26 23:49:05 WARN RowBasedKeyValueBatch: Calling spill() on RowBasedKeyValueBatch. Will not spill but return 0.


    [Stage 32:=============================>                            (1 + 1) / 2]

    22/10/26 23:49:19 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB
    +-----+------+
    |label| count|
    +-----+------+
    |  0.0|560264|
    |  1.0|560405|
    +-----+------+
    


                                                                                    

## Training the Model


```python
from pyspark.ml.classification import LogisticRegression
```


```python
lr = LogisticRegression(labelCol = "label", featuresCol = "features",maxIter = 10)
model = lr.fit(trainDF) # Yes its just one line! every ML is just "Fit" ;)
```

    22/10/26 23:50:43 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB


                                                                                    

    22/10/26 23:51:35 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB


    [Stage 36:>                                                         (0 + 2) / 2]

    22/10/26 23:52:27 WARN InstanceBuilder$NativeBLAS: Failed to load implementation from:dev.ludovic.netlib.blas.JNIBLAS
    22/10/26 23:52:27 WARN InstanceBuilder$NativeBLAS: Failed to load implementation from:dev.ludovic.netlib.blas.ForeignLinkerBLAS


                                                                                    

    22/10/26 23:52:29 WARN BLAS: Failed to load implementation from: com.github.fommil.netlib.NativeSystemBLAS
    22/10/26 23:52:29 WARN BLAS: Failed to load implementation from: com.github.fommil.netlib.NativeRefBLAS
    22/10/26 23:52:29 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB
    22/10/26 23:52:30 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB


                                                                                    

    22/10/26 23:52:31 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB


                                                                                    

    22/10/26 23:52:31 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB
    22/10/26 23:52:32 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB


                                                                                    

    22/10/26 23:52:32 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB
    22/10/26 23:52:33 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB
    22/10/26 23:52:33 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB
    22/10/26 23:52:34 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB
    22/10/26 23:52:34 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB



```python
predictions = model.transform(testDF)
pred = predictions.toPandas()
pred.head()
```

    22/10/26 23:59:11 WARN DAGScheduler: Broadcasting large task binary with size 8.8 MiB


                                                                                    




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>label</th>
      <th>features</th>
      <th>rawPrediction</th>
      <th>probability</th>
      <th>prediction</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.0</td>
      <td>(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...</td>
      <td>[-0.25373338853954264, 0.25373338853954264]</td>
      <td>[0.43690479927451065, 0.5630952007254894]</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.0</td>
      <td>(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...</td>
      <td>[-0.25373338853954264, 0.25373338853954264]</td>
      <td>[0.43690479927451065, 0.5630952007254894]</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.0</td>
      <td>(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...</td>
      <td>[-0.25373338853954264, 0.25373338853954264]</td>
      <td>[0.43690479927451065, 0.5630952007254894]</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.0</td>
      <td>(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...</td>
      <td>[-0.25373338853954264, 0.25373338853954264]</td>
      <td>[0.43690479927451065, 0.5630952007254894]</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.0</td>
      <td>(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...</td>
      <td>[-0.25373338853954264, 0.25373338853954264]</td>
      <td>[0.43690479927451065, 0.5630952007254894]</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>



## Evaluation


```python
# Total_True = predictions.filter(predictions['prediction']==predictions['label']).count()
# Alldata = predictions.count()
# Accuracy = Total_True/Alldata
# print("Accuracy Score is:", Accuracy*100, '%')
```

    22/10/27 00:08:24 WARN DAGScheduler: Broadcasting large task binary with size 8.8 MiB


                                                                                    

    22/10/27 00:09:17 WARN DAGScheduler: Broadcasting large task binary with size 6.8 MiB


    [Stage 51:=============================>                            (1 + 1) / 2]

    Accuracy Score is: 75.96566881758116 %


                                                                                    


```python
y_true = pred['label'].astype('float')
y_pred = pred['prediction']
```


```python
from sklearn.metrics import classification_report, confusion_matrix
print(classification_report(y_true, y_pred))
```

                  precision    recall  f1-score   support
    
             0.0       0.77      0.74      0.76    239736
             1.0       0.75      0.77      0.76    239595
    
        accuracy                           0.76    479331
       macro avg       0.76      0.76      0.76    479331
    weighted avg       0.76      0.76      0.76    479331
    


