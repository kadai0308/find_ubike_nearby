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

