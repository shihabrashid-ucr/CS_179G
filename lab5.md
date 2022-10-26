# CS 179G Lab 5

# PySpark with Machine Learning
https://www.kaggle.com/code/diniftikhar025/sentimentanalysiswithlogisticregressioninpyspark
https://www.kaggle.com/code/nezarabdilahprakasa/sentiment-analysis-using-pyspark-big-data/notebook
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
