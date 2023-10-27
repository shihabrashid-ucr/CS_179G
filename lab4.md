# CS 179G Lab 4
## User Defined Functions
Learn about UDF [here](https://sparkbyexamples.com/pyspark/pyspark-udf-user-defined-function/)
Task: Add 100 to all values of "fixed acidity" from previous lab
1. Create a python function for the task
```python
def add_100():
```
2. Register and use UDF
```python
from pyspark.sql.functions import col, udf
from pyspark.sql.types import FloatType()
add_hundred_UDF = udf(lambda z:add_100(z),FloatType())   
df.withColumn("Cureated Name", upperCaseUDF(col("fixed acidity"))) \
  .show(10)
```

## Download Tweets data
1. Install [gdown](https://github.com/wkentaro/gdown)
    ```bash
    # In virtual environment
    python3 -m pip install gdown
    ```
2. Download Tweet data
    ```bash
    if [[ ! -d ~/lab4 ]]; then
      mkdir ~/lab4
    fi
    cd ~/lab4
    # In virtual environment
	if [[ ! -f ~/lab4/geoTwitter21-07-04.zip ]]; then
      gdown https://drive.google.com/uc?id=1j-ik6M1HR3gWkL56aWvnsuTe_wWXAbKQ
	fi
    ```
3. Check file contents (~8.3 GB raw text)
    ```bash
    sudo apt-get install -y unzip
    unzip -l geoTwitter21-07-04.zip
    ```
    Output
    ```
    Archive:  geoTwitter21-07-04.zip
      Length      Date    Time    Name
    ---------  ---------- -----   ----
    356057339  2021-07-03 18:03   geoTwitter21-07-04/geoTwitter21-07-04_00:00
    365983516  2021-07-03 19:04   geoTwitter21-07-04/geoTwitter21-07-04_01:00
    381720510  2021-07-03 20:05   geoTwitter21-07-04/geoTwitter21-07-04_02:00
    380904015  2021-07-03 21:05   geoTwitter21-07-04/geoTwitter21-07-04_03:00
    313963902  2021-07-03 22:06   geoTwitter21-07-04/geoTwitter21-07-04_04:00
    293205539  2021-07-03 23:07   geoTwitter21-07-04/geoTwitter21-07-04_05:00
    283025242  2021-07-04 00:08   geoTwitter21-07-04/geoTwitter21-07-04_06:00
    289566019  2021-07-04 01:08   geoTwitter21-07-04/geoTwitter21-07-04_07:00
    300578095  2021-07-04 02:09   geoTwitter21-07-04/geoTwitter21-07-04_08:00
    310253192  2021-07-04 03:10   geoTwitter21-07-04/geoTwitter21-07-04_09:00
    317564070  2021-07-04 04:11   geoTwitter21-07-04/geoTwitter21-07-04_10:00
    351335213  2021-07-04 05:11   geoTwitter21-07-04/geoTwitter21-07-04_11:00
    385393649  2021-07-04 05:57   geoTwitter21-07-04/geoTwitter21-07-04_12:00
    431499183  2021-07-04 06:58   geoTwitter21-07-04/geoTwitter21-07-04_13:00
    465459092  2021-07-04 07:58   geoTwitter21-07-04/geoTwitter21-07-04_14:00
    462982212  2021-07-04 08:59   geoTwitter21-07-04/geoTwitter21-07-04_15:00
    461191043  2021-07-04 10:00   geoTwitter21-07-04/geoTwitter21-07-04_16:00
    441517713  2021-07-04 11:01   geoTwitter21-07-04/geoTwitter21-07-04_17:00
    420419790  2021-07-04 12:01   geoTwitter21-07-04/geoTwitter21-07-04_18:00
    415226346  2021-07-04 13:02   geoTwitter21-07-04/geoTwitter21-07-04_19:00
    413862207  2021-07-04 14:03   geoTwitter21-07-04/geoTwitter21-07-04_20:00
    398302862  2021-07-04 15:03   geoTwitter21-07-04/geoTwitter21-07-04_21:00
    352998772  2021-07-04 16:04   geoTwitter21-07-04/geoTwitter21-07-04_22:00
    330738842  2021-07-04 17:00   geoTwitter21-07-04/geoTwitter21-07-04_23:00
    ---------                     -------
    8923748363                     24 files
    ```
4. Check available memory and disk space
    - Memory
        ```bash
        free -h
        ```
        Output
        ```
                      total        used        free      shared  buff/cache   available
        Mem:          3.8Gi       699Mi       205Mi       0.0Ki       3.0Gi       2.9Gi
        Swap:            0B          0B          0B
        ```
    - Disk space
        ```bash
        df -h
        ```
        Output
        ```
        Filesystem      Size  Used Avail Use% Mounted on
        /dev/root       7.7G  4.3G  3.5G  56% /
        devtmpfs        2.0G     0  2.0G   0% /dev
        tmpfs           2.0G     0  2.0G   0% /dev/shm
        tmpfs           393M  856K  393M   1% /run
        tmpfs           5.0M     0  5.0M   0% /run/lock
        tmpfs           2.0G     0  2.0G   0% /sys/fs/cgroup
        /dev/loop0       34M   34M     0 100% /snap/amazon-ssm-agent/3552
        /dev/loop1       25M   25M     0 100% /snap/amazon-ssm-agent/4046
        /dev/loop2       56M   56M     0 100% /snap/core18/2128
        /dev/loop3       56M   56M     0 100% /snap/core18/1997
        /dev/loop4       62M   62M     0 100% /snap/core20/1081
        /dev/loop5       68M   68M     0 100% /snap/lxd/21545
        /dev/loop6       71M   71M     0 100% /snap/lxd/19647
        /dev/loop7       33M   33M     0 100% /snap/snapd/13170
        /dev/loop9       62M   62M     0 100% /snap/core20/1169
        /dev/loop10      33M   33M     0 100% /snap/snapd/13270
        tmpfs           393M     0  393M   0% /run/user/1000
        ```

## File content preview
Reference: [https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/overview](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/overview)

```python
import zipfile

PREFIX = "geoTwitter21-07-04"
with zipfile.ZipFile(f"/home/ubuntu/lab4/{PREFIX}.zip", "r") as zf:
    # Open the first file only
    with zf.open(f"{PREFIX}/{PREFIX}_00:00") as f:
        # Raw content of the first line
        print(f.readline())
```
Output
```
b'{"created_at":"Sun Jul 04 00:00:00 +0000 2021","id":1411474838342959106,"id_str":"1411474838342959106","text":"\\u53d6\\u3063\\u3066\\u3068\\u3063\\u305f\\u3089\\u3044\\u3044\\u611f\\u3058\\u306b\\u306a\\u308a\\u305d\\u3046ww\\n\\u898b\\u305f\\u77ac\\u9593\\u7b11\\u3063\\u3066\\u3057\\u307e\\u3063\\u305f\\u7b11","source":"\\u003ca href=\\"http:\\/\\/twitter.com\\/download\\/iphone\\" rel=\\"nofollow\\"\\u003eTwitter for iPhone\\u003c\\/a\\u003e","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":1220917476088659970,"id_str":"1220917476088659970","name":"ODYSUKE","screen_name":"odysuke1729","location":"\\u57fc\\u7389 \\u6240\\u6ca2\\u5e02","url":null,"description":"\\u3088\\u308d\\u3057\\u304f\\u304a\\u306d\\u304c\\u3044\\u3057\\u307e\\u3059\\uff01\\uff01\\uff01\\u57fc\\u7389\\u5728\\u4f4f32\\u6b73\\uff08\\u7b11\\uff09\\u8eca\\u597d\\u304d\\u306a\\u5857\\u88c5\\u5c4b\\u3067\\u3059\\u3002\\u8eca\\u597d\\u304d\\u3055\\u3093\\u3068\\u4ef2\\u826f\\u304f\\u306a\\u308a\\u305f\\u3044\\u3002\\u3002RB1\\u30aa\\u30c7\\u30c3\\u30bb\\u30a4\\u4e57\\u3063\\u3066\\u307e\\u3059\\u3002\\u3002\\u263a\\ufe0f\\ud83d\\udc4d\\u3088\\u308d\\u3057\\u304f\\u304a\\u9858\\u3044\\u3057\\u307e\\u3059\\uff01\\uff01\\u611a\\u75f4\\u5410\\u304d\\u307e\\u3059\\uff08\\u7b11\\uff09","translator_type":"none","protected":false,"verified":false,"followers_count":83,"friends_count":53,"listed_count":0,"favourites_count":2162,"statuses_count":598,"created_at":"Sat Jan 25 03:53:12 +0000 2020","utc_offset":null,"time_zone":null,"geo_enabled":true,"lang":null,"contributors_enabled":false,"is_translator":false,"profile_background_color":"F5F8FA","profile_background_image_url":"","profile_background_image_url_https":"","profile_background_tile":false,"profile_link_color":"1DA1F2","profile_sidebar_border_color":"C0DEED","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":true,"profile_image_url":"http:\\/\\/pbs.twimg.com\\/profile_images\\/1375361181775405056\\/NkfrAsyt_normal.jpg","profile_image_url_https":"https:\\/\\/pbs.twimg.com\\/profile_images\\/1375361181775405056\\/NkfrAsyt_normal.jpg","profile_banner_url":"https:\\/\\/pbs.twimg.com\\/profile_banners\\/1220917476088659970\\/1616746716","default_profile":true,"default_profile_image":false,"following":null,"follow_request_sent":null,"notifications":null,"withheld_in_countries":[]},"geo":null,"coordinates":null,"place":{"id":"1d5d82d43a574e4f","url":"https:\\/\\/api.twitter.com\\/1.1\\/geo\\/id\\/1d5d82d43a574e4f.json","place_type":"city","name":"Tokorozawa-shi","full_name":"Tokorozawa-shi, Saitama","country_code":"JP","country":"Japan","bounding_box":{"type":"Polygon","coordinates":[[[139.379107,35.763076],[139.379107,35.843832],[139.545964,35.843832],[139.545964,35.763076]]]},"attributes":{}},"contributors":null,"quoted_status_id":1410779794384384001,"quoted_status_id_str":"1410779794384384001","quoted_status":{"created_at":"Fri Jul 02 01:58:08 +0000 2021","id":1410779794384384001,"id_str":"1410779794384384001","text":"\\u30de\\u30ad\\u30bf\\u306e\\u4e0a\\u7f6e\\u304d\\u30bf\\u30fc\\u30d3\\u30f3www https:\\/\\/t.co\\/ZvXh6sjzno","display_text_range":[0,14],"source":"\\u003ca href=\\"http:\\/\\/twitter.com\\/download\\/android\\" rel=\\"nofollow\\"\\u003eTwitter for Android\\u003c\\/a\\u003e","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":2949846150,"id_str":"2949846150","name":"masiro","screen_name":"masiro_er34","location":"\\u6803\\u6728\\u306e\\u30d6\\u30ea\\u30ea\\u30a2\\u30f3\\u30c8\\u30d1\\u30fc\\u30af","url":null,"description":"ER34\\u4e57\\u3063\\u3066\\u307e\\u3059\\u3002  \\u6803\\u6728\\u3067\\u8d70\\u3063\\u3066\\u307e\\u3059\\u3002  \\u7121\\u8a00\\u30d5\\u30a9\\u30ed\\u30fc\\u3057\\u3083\\u30fc\\u305b\\u3093\\uff01\\u30d5\\u30a9\\u30ed\\u30fc\\u8fd4\\u3059\\u306e\\u9045\\u3044\\u3068\\u304d\\u3042\\u308a\\u307e\\u3059m(_ _)m","translator_type":"none","protected":false,"verified":false,"followers_count":1240,"friends_count":1019,"listed_count":10,"favourites_count":79400,"statuses_count":17287,"created_at":"Mon Dec 29 10:31:09 +0000 2014","utc_offset":null,"time_zone":null,"geo_enabled":true,"lang":null,"contributors_enabled":false,"is_translator":false,"profile_background_color":"C0DEED","profile_background_image_url":"http:\\/\\/abs.twimg.com\\/images\\/themes\\/theme1\\/bg.png","profile_background_image_url_https":"https:\\/\\/abs.twimg.com\\/images\\/themes\\/theme1\\/bg.png","profile_background_tile":false,"profile_link_color":"1DA1F2","profile_sidebar_border_color":"C0DEED","profile_sidebar_fill_color":"DDEEF6","profile_text_color":"333333","profile_use_background_image":true,"profile_image_url":"http:\\/\\/pbs.twimg.com\\/profile_images\\/1327942484425465857\\/lmNSAr4u_normal.jpg","profile_image_url_https":"https:\\/\\/pbs.twimg.com\\/profile_images\\/1327942484425465857\\/lmNSAr4u_normal.jpg","profile_banner_url":"https:\\/\\/pbs.twimg.com\\/profile_banners\\/2949846150\\/1524072616","default_profile":true,"default_profile_image":false,"following":null,"follow_request_sent":null,"notifications":null,"withheld_in_countries":[]},"geo":null,"coordinates":null,"place":null,"contributors":null,"is_quote_status":false,"quote_count":9,"reply_count":4,"retweet_count":151,"favorite_count":1406,"entities":{"hashtags":[],"urls":[],"user_mentions":[],"symbols":[],"media":[{"id":1410779785949634560,"id_str":"1410779785949634560","indices":[15,38],"media_url":"http:\\/\\/pbs.twimg.com\\/media\\/E5QYvZ3UYAAvfMT.jpg","media_url_https":"https:\\/\\/pbs.twimg.com\\/media\\/E5QYvZ3UYAAvfMT.jpg","url":"https:\\/\\/t.co\\/ZvXh6sjzno","display_url":"pic.twitter.com\\/ZvXh6sjzno","expanded_url":"https:\\/\\/twitter.com\\/masiro_er34\\/status\\/1410779794384384001\\/photo\\/1","type":"photo","sizes":{"thumb":{"w":150,"h":150,"resize":"crop"},"medium":{"w":584,"h":1200,"resize":"fit"},"small":{"w":331,"h":680,"resize":"fit"},"large":{"w":996,"h":2048,"resize":"fit"}}}]},"extended_entities":{"media":[{"id":1410779785949634560,"id_str":"1410779785949634560","indices":[15,38],"media_url":"http:\\/\\/pbs.twimg.com\\/media\\/E5QYvZ3UYAAvfMT.jpg","media_url_https":"https:\\/\\/pbs.twimg.com\\/media\\/E5QYvZ3UYAAvfMT.jpg","url":"https:\\/\\/t.co\\/ZvXh6sjzno","display_url":"pic.twitter.com\\/ZvXh6sjzno","expanded_url":"https:\\/\\/twitter.com\\/masiro_er34\\/status\\/1410779794384384001\\/photo\\/1","type":"photo","sizes":{"thumb":{"w":150,"h":150,"resize":"crop"},"medium":{"w":584,"h":1200,"resize":"fit"},"small":{"w":331,"h":680,"resize":"fit"},"large":{"w":996,"h":2048,"resize":"fit"}}}]},"favorited":false,"retweeted":false,"possibly_sensitive":false,"filter_level":"low","lang":"ja"},"quoted_status_permalink":{"url":"https:\\/\\/t.co\\/5IH3m7zQC5","expanded":"https:\\/\\/twitter.com\\/masiro_er34\\/status\\/1410779794384384001","display":"twitter.com\\/masiro_er34\\/st\\u2026"},"is_quote_status":true,"quote_count":0,"reply_count":0,"retweet_count":0,"favorite_count":0,"entities":{"hashtags":[],"urls":[],"user_mentions":[],"symbols":[]},"favorited":false,"retweeted":false,"filter_level":"low","lang":"ja","timestamp_ms":"1625356800052"}\n'
```
Since it's JSON format (`bytes`, not `str`), print it to more human-readable format
```python
import json
import zipfile

PREFIX = "geoTwitter21-07-04"
with zipfile.ZipFile(f"/home/ubuntu/lab4/{PREFIX}.zip", "r") as zf:
    # Open the first file only
    with zf.open(f"{PREFIX}/{PREFIX}_00:00") as f:
        js = json.loads(f.readline())
        print(json.dumps(js, indent=2, sort_keys=True))
```
Output
```json
{
  "contributors": null,
  "coordinates": null,
  "created_at": "Sun Jul 04 00:00:00 +0000 2021",
  "entities": {
    "hashtags": [],
    "symbols": [],
    "urls": [],
    "user_mentions": []
  },
  "favorite_count": 0,
  "favorited": false,
  "filter_level": "low",
  "geo": null,
  "id": 1411474838342959106,
  "id_str": "1411474838342959106",
  "in_reply_to_screen_name": null,
  "in_reply_to_status_id": null,
  "in_reply_to_status_id_str": null,
  "in_reply_to_user_id": null,
  "in_reply_to_user_id_str": null,
  "is_quote_status": true,
  "lang": "ja",
  "place": {
    "attributes": {},
    "bounding_box": {
      "coordinates": [
        [
          [
            139.379107,
            35.763076
          ],
          [
            139.379107,
            35.843832
          ],
          [
            139.545964,
            35.843832
          ],
          [
            139.545964,
            35.763076
          ]
        ]
      ],
      "type": "Polygon"
    },
    "country": "Japan",
    "country_code": "JP",
    "full_name": "Tokorozawa-shi, Saitama",
    "id": "1d5d82d43a574e4f",
    "name": "Tokorozawa-shi",
    "place_type": "city",
    "url": "https://api.twitter.com/1.1/geo/id/1d5d82d43a574e4f.json"
  },
  "quote_count": 0,
  "quoted_status": {
    "contributors": null,
    "coordinates": null,
    "created_at": "Fri Jul 02 01:58:08 +0000 2021",
    "display_text_range": [
      0,
      14
    ],
    "entities": {
      "hashtags": [],
      "media": [
        {
          "display_url": "pic.twitter.com/ZvXh6sjzno",
          "expanded_url": "https://twitter.com/masiro_er34/status/1410779794384384001/photo/1",
          "id": 1410779785949634560,
          "id_str": "1410779785949634560",
          "indices": [
            15,
            38
          ],
          "media_url": "http://pbs.twimg.com/media/E5QYvZ3UYAAvfMT.jpg",
          "media_url_https": "https://pbs.twimg.com/media/E5QYvZ3UYAAvfMT.jpg",
          "sizes": {
            "large": {
              "h": 2048,
              "resize": "fit",
              "w": 996
            },
            "medium": {
              "h": 1200,
              "resize": "fit",
              "w": 584
            },
            "small": {
              "h": 680,
              "resize": "fit",
              "w": 331
            },
            "thumb": {
              "h": 150,
              "resize": "crop",
              "w": 150
            }
          },
          "type": "photo",
          "url": "https://t.co/ZvXh6sjzno"
        }
      ],
      "symbols": [],
      "urls": [],
      "user_mentions": []
    },
    "extended_entities": {
      "media": [
        {
          "display_url": "pic.twitter.com/ZvXh6sjzno",
          "expanded_url": "https://twitter.com/masiro_er34/status/1410779794384384001/photo/1",
          "id": 1410779785949634560,
          "id_str": "1410779785949634560",
          "indices": [
            15,
            38
          ],
          "media_url": "http://pbs.twimg.com/media/E5QYvZ3UYAAvfMT.jpg",
          "media_url_https": "https://pbs.twimg.com/media/E5QYvZ3UYAAvfMT.jpg",
          "sizes": {
            "large": {
              "h": 2048,
              "resize": "fit",
              "w": 996
            },
            "medium": {
              "h": 1200,
              "resize": "fit",
              "w": 584
            },
            "small": {
              "h": 680,
              "resize": "fit",
              "w": 331
            },
            "thumb": {
              "h": 150,
              "resize": "crop",
              "w": 150
            }
          },
          "type": "photo",
          "url": "https://t.co/ZvXh6sjzno"
        }
      ]
    },
    "favorite_count": 1406,
    "favorited": false,
    "filter_level": "low",
    "geo": null,
    "id": 1410779794384384001,
    "id_str": "1410779794384384001",
    "in_reply_to_screen_name": null,
    "in_reply_to_status_id": null,
    "in_reply_to_status_id_str": null,
    "in_reply_to_user_id": null,
    "in_reply_to_user_id_str": null,
    "is_quote_status": false,
    "lang": "ja",
    "place": null,
    "possibly_sensitive": false,
    "quote_count": 9,
    "reply_count": 4,
    "retweet_count": 151,
    "retweeted": false,
    "source": "<a href=\"http://twitter.com/download/android\" rel=\"nofollow\">Twitter for Android</a>",
    "text": "\u30de\u30ad\u30bf\u306e\u4e0a\u7f6e\u304d\u30bf\u30fc\u30d3\u30f3www https://t.co/ZvXh6sjzno",
    "truncated": false,
    "user": {
      "contributors_enabled": false,
      "created_at": "Mon Dec 29 10:31:09 +0000 2014",
      "default_profile": true,
      "default_profile_image": false,
      "description": "ER34\u4e57\u3063\u3066\u307e\u3059\u3002  \u6803\u6728\u3067\u8d70\u3063\u3066\u307e\u3059\u3002  \u7121\u8a00\u30d5\u30a9\u30ed\u30fc\u3057\u3083\u30fc\u305b\u3093\uff01\u30d5\u30a9\u30ed\u30fc\u8fd4\u3059\u306e\u9045\u3044\u3068\u304d\u3042\u308a\u307e\u3059m(_ _)m",
      "favourites_count": 79400,
      "follow_request_sent": null,
      "followers_count": 1240,
      "following": null,
      "friends_count": 1019,
      "geo_enabled": true,
      "id": 2949846150,
      "id_str": "2949846150",
      "is_translator": false,
      "lang": null,
      "listed_count": 10,
      "location": "\u6803\u6728\u306e\u30d6\u30ea\u30ea\u30a2\u30f3\u30c8\u30d1\u30fc\u30af",
      "name": "masiro",
      "notifications": null,
      "profile_background_color": "C0DEED",
      "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
      "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
      "profile_background_tile": false,
      "profile_banner_url": "https://pbs.twimg.com/profile_banners/2949846150/1524072616",
      "profile_image_url": "http://pbs.twimg.com/profile_images/1327942484425465857/lmNSAr4u_normal.jpg",
      "profile_image_url_https": "https://pbs.twimg.com/profile_images/1327942484425465857/lmNSAr4u_normal.jpg",
      "profile_link_color": "1DA1F2",
      "profile_sidebar_border_color": "C0DEED",
      "profile_sidebar_fill_color": "DDEEF6",
      "profile_text_color": "333333",
      "profile_use_background_image": true,
      "protected": false,
      "screen_name": "masiro_er34",
      "statuses_count": 17287,
      "time_zone": null,
      "translator_type": "none",
      "url": null,
      "utc_offset": null,
      "verified": false,
      "withheld_in_countries": []
    }
  },
  "quoted_status_id": 1410779794384384001,
  "quoted_status_id_str": "1410779794384384001",
  "quoted_status_permalink": {
    "display": "twitter.com/masiro_er34/st\u2026",
    "expanded": "https://twitter.com/masiro_er34/status/1410779794384384001",
    "url": "https://t.co/5IH3m7zQC5"
  },
  "reply_count": 0,
  "retweet_count": 0,
  "retweeted": false,
  "source": "<a href=\"http://twitter.com/download/iphone\" rel=\"nofollow\">Twitter for iPhone</a>",
  "text": "\u53d6\u3063\u3066\u3068\u3063\u305f\u3089\u3044\u3044\u611f\u3058\u306b\u306a\u308a\u305d\u3046ww\n\u898b\u305f\u77ac\u9593\u7b11\u3063\u3066\u3057\u307e\u3063\u305f\u7b11",
  "timestamp_ms": "1625356800052",
  "truncated": false,
  "user": {
    "contributors_enabled": false,
    "created_at": "Sat Jan 25 03:53:12 +0000 2020",
    "default_profile": true,
    "default_profile_image": false,
    "description": "\u3088\u308d\u3057\u304f\u304a\u306d\u304c\u3044\u3057\u307e\u3059\uff01\uff01\uff01\u57fc\u7389\u5728\u4f4f32\u6b73\uff08\u7b11\uff09\u8eca\u597d\u304d\u306a\u5857\u88c5\u5c4b\u3067\u3059\u3002\u8eca\u597d\u304d\u3055\u3093\u3068\u4ef2\u826f\u304f\u306a\u308a\u305f\u3044\u3002\u3002RB1\u30aa\u30c7\u30c3\u30bb\u30a4\u4e57\u3063\u3066\u307e\u3059\u3002\u3002\u263a\ufe0f\ud83d\udc4d\u3088\u308d\u3057\u304f\u304a\u9858\u3044\u3057\u307e\u3059\uff01\uff01\u611a\u75f4\u5410\u304d\u307e\u3059\uff08\u7b11\uff09",
    "favourites_count": 2162,
    "follow_request_sent": null,
    "followers_count": 83,
    "following": null,
    "friends_count": 53,
    "geo_enabled": true,
    "id": 1220917476088659970,
    "id_str": "1220917476088659970",
    "is_translator": false,
    "lang": null,
    "listed_count": 0,
    "location": "\u57fc\u7389 \u6240\u6ca2\u5e02",
    "name": "ODYSUKE",
    "notifications": null,
    "profile_background_color": "F5F8FA",
    "profile_background_image_url": "",
    "profile_background_image_url_https": "",
    "profile_background_tile": false,
    "profile_banner_url": "https://pbs.twimg.com/profile_banners/1220917476088659970/1616746716",
    "profile_image_url": "http://pbs.twimg.com/profile_images/1375361181775405056/NkfrAsyt_normal.jpg",
    "profile_image_url_https": "https://pbs.twimg.com/profile_images/1375361181775405056/NkfrAsyt_normal.jpg",
    "profile_link_color": "1DA1F2",
    "profile_sidebar_border_color": "C0DEED",
    "profile_sidebar_fill_color": "DDEEF6",
    "profile_text_color": "333333",
    "profile_use_background_image": true,
    "protected": false,
    "screen_name": "odysuke1729",
    "statuses_count": 598,
    "time_zone": null,
    "translator_type": "none",
    "url": null,
    "utc_offset": null,
    "verified": false,
    "withheld_in_countries": []
  }
}
```

## Task 1: Find Tweet with largest `user`:`favourites_count`

### Method 1: In memory processing
1. Read and store `favourites_count` from all Tweets from all files into a `list`
2. Return the `max()` from the list

OK if total data size is small, and only the largest is needed. If Tweet is needed, make a second pass to return the Tweet with the largest value.

```python
import json
import zipfile

PREFIX = "geoTwitter21-07-04"


def read_tweets(max_cnt=-1):
    fc_counts = []
    with zipfile.ZipFile(f"/home/ubuntu/lab4/{PREFIX}.zip", "r") as zf:
        for hour in range(24):
            with zf.open(f"{PREFIX}/{PREFIX}_{hour:02d}:00") as f:
                for line in f:
                    line = line.decode("utf-8").rstrip("\n")
                    if not line:
                        continue # Skip empty lines
                    js = json.loads(line)
                    fc = int(js["user"]["favourites_count"])
                    if max_cnt == -1:
                        fc_counts.append(fc)
                    elif fc == max_cnt:
                        print(max_cnt)
                        print(js)
                        return
    read_tweets(max(fc_counts))


read_tweets()
```

### Method 2: Manual scan
Requires minimum memory, one pass solution.
```python
import json
import zipfile

PREFIX = "geoTwitter21-07-04"
fc_cnt = -1
tweet = None
with zipfile.ZipFile(f"/home/ubuntu/lab4/{PREFIX}.zip", "r") as zf:
    for hour in range(24):
        with zf.open(f"{PREFIX}/{PREFIX}_{hour:02d}:00") as f:
            for line in f:
                line = line.decode("utf-8").rstrip("\n")
                if not line:
                    continue # Skip empty lines
                js = json.loads(line)
                fc = int(js["user"]["favourites_count"])
                if fc > fc_cnt:
                    fc_cnt = fc
                    tweet = js
print(fc_cnt)
print(tweet)
```

## Task 2: Find the most frequent place (`place`:`country_code`)
### Method 1: In memory counting via `dict`
```python
import json
import zipfile

PREFIX = "geoTwitter21-07-04"
freqs = {}
with zipfile.ZipFile(f"/home/ubuntu/lab4/{PREFIX}.zip", "r") as zf:
    for hour in range(24):
        with zf.open(f"{PREFIX}/{PREFIX}_{hour:02d}:00") as f:
            for line in f:
                line = line.decode("utf-8").rstrip("\n")
                if not line:
                    continue # Skip empty lines
                js = json.loads(line)
                if js["place"] is None or js["place"]["country_code"] is None:
                    continue # Skip Tweets with no `place`/`country_code` tag
                code = js["place"]["country_code"]
                if code:
                    freqs[code] = freqs.get(code, 0) + 1
max_code = None
max_freq = -1
for code, freq in freqs.items():
    if freq > max_freq:
        max_code = code
        max_freq = freq
print(max_code)
print(max_freq)
```

### Method 2: External sorting
1. Save the country code into a temporary file
2. Use Linux commands `sort` and `uniq` (`sort` command does merge-sort)

```python
import json
import zipfile

PREFIX = "geoTwitter21-07-04"
with zipfile.ZipFile(f"/home/ubuntu/lab4/{PREFIX}.zip", "r") as zf, \
        open("/home/ubuntu/lab4/country_codes.txt", "w") as cf:
    for hour in range(24):
        with zf.open(f"{PREFIX}/{PREFIX}_{hour:02d}:00") as f:
            for line in f:
                line = line.decode("utf-8").rstrip("\n")
                if not line:
                    continue # Skip empty lines
                js = json.loads(line)
                if js["place"] is None or js["place"]["country_code"] is None:
                    continue # Skip Tweets with no `place` / `country_code` tag
                code = js["place"]["country_code"]
                if code:
                    cf.write(code + "\n")
```
External sorting and counting
```bash
# head -n 5: print the first5 lines (largest 5)
sort ~/lab4/country_codes.txt | uniq -c | sort -nr | head -n 5
```

### Method 3: PySpark MapReduce
Reference: [https://pythonexamples.org/pyspark-word-count-example/](https://pythonexamples.org/pyspark-word-count-example/)
```python
from pyspark import SparkContext, SparkConf

sc = SparkContext("local", "Most Frequent Countries")
codes = sc.textFile("/home/ubuntu/lab4/country_codes.txt")
cc_cnts = codes.map(lambda cc: (cc, 1)).reduceByKey(lambda a, b: a + b)
cc_cnts.saveAsTextFile("/home/ubuntu/lab4/results")
```

### Build a WordCloud
Install wordcloud library
```
pip3 install wordcloud
```

Run wordcloud on the tweets, use following code as template to generate wordcloud.
```python
import matplotlib.pyplot as plt
from wordcloud import WordCloud
text = "This is a random tweet, with random words, that makes no sense with random"
# Creating word_cloud with text as argument in .generate() method
word_cloud = WordCloud(collocations = False, background_color = 'white').generate(text)
# Display the generated Word Cloud
plt.imshow(word_cloud, interpolation='bilinear')
plt.axis("off")
plt.show()
```
