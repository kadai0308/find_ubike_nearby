find ubike nearby
=========

RESTful API to find 2 nearest ubike stations in Taipei

Update sbi(num of ubikes) of ubike stations every 10 sec automatically

project url: https://find-ubike-nearby.herokuapp.com//v1/ubike-station/taipei?lat={latitude}&lng={longitude}

## how i get ubike data

  crawl data from http://taipei.youbike.com.tw/cht/f12.php
  
  ### first step
  
  find render function in script
    
  ![find render function](https://i.imgur.com/lLIuDWM.png)
  
  ### second step
  
  find data resource
  
  ![find data resource](https://i.imgur.com/7JWkJfL.png)
  
## how i find the 2 nearest ubike station

  Prepare 1. 
    decide the width and height of every box, and segment the whole Taipei by boxes.
  
  
  Prepare 2. 
    Classify the ubike station belong which box, according to the location of ubike station.
  
  
  Step 1. 
    find the current location in which box
  
  
  Step 2. 
    Get all ubike stations around the current location box. If the amount less than 2, get the box out around.
    
    ex: current location in box(11, 3), get ubike stations with ubike in [ box(10, 2), box(10, 3), box(10, 4) ... box(12, 4) ]
    until amount of stations list > 2
    
   Step 3. 
    find the 2 nearest station from the stations list in Step 2
    
```
  怕我的英文太破, 所以用中文簡短的解釋一遍：
  
    事前準備： 把整個台北分成好幾個方格, 把每個 ubike 站都依照位置分類到相對應的方格去
    
    拿到現在的位置資訊之後先找出在哪一格方格之中, 
    
    從資料庫把周圍一圈的 ubike 站（有車的）都拿出來, 
    
    如果總數超過兩站就可以停了, 不夠的話就在往外一圈拿
    
    拿完之後就可以算最近的兩站了, 這樣就不用把全部的車站都算過一遍了
    
```  
    


  ![Taipei](https://i.imgur.com/5EiFHX9.png)
  

## Spec

  -  1: all ubike stations are full
  -  0: OK
  - -1: invalid latitude or longitude
  - -2: given location not in Taipei City
  - -3: system error

### Response format:

  type: ```application/json```

  ```
  {
      "code": $error-code,
      "result": [
          {
             "station": "$name-of-station", 
             "num_ubike": $number-of-available-ubike
          },
          {
             "station": "$name-of-station", 
             "num_ubike": $number-of-available-ubike
          }
      ]
  }
  ```

## logs

  ### logs format example:

  (store in api/logs/error.log)
  ```
  level: ERROR 
  time: 2017-04-10 02:06:05,222 
  path: /find_ubike_nearby/api/views.py 
  message: 'dict' object has no attribute 'lat'
  ```

  ### logs setting:

  ```
  LOGGING = {
      'version': 1,
      'formatters': {
          'verbose': {
              'format': 'level: %(levelname)s \ntime: %(asctime)s \npath: %(pathname)s \nmessage: %(message)s\n'
          },
          'simple': {
              'format': '%(levelname)s %(message)s'
          },
      },
      'handlers': {
          'file': {
              'level': 'DEBUG',
              'class': 'logging.FileHandler',
              'filename': 'api/logs/error.log',
              'formatter': 'verbose'
          },
      },
      'loggers': {
          'api.views': {
              'handlers': ['file'],
              'level': 'ERROR',
              'propagate': True,  
          }
      }
  }
  ```

## test

  ```
  python manage.py test api.tests
  ```

