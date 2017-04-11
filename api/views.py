from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse

from api.models import City, CityBox, UbikeStat

# built in package
import logging
from decimal import *
import urllib
import sys
import heapq
import datetime
import time
import json

# pip package 
import requests
import django_rq

WIDTH = Decimal('0.0104332')
HEIGHT = Decimal('0.0125203')
logger = logging.getLogger(__name__)

def parse_stat_data (request):
    # setting data
    City.objects.create(
        name = 'taipei',
        l_lat = Decimal('25.210380'),
        l_lng = Decimal('121.457156'),
        r_lat = Decimal('24.959974'),
        r_lng = Decimal('121.665821')
    )

    city = City.objects.get(name = 'taipei')
    for i in range(20):
        for j in range(20):
            CityBox.objects.create(row = i, col = j, city = city)

    content = requests.get('http://taipei.youbike.com.tw/cht/f12.php').content
    # get arealist
    web_content = str(requests.get('http://taipei.youbike.com.tw/cht/f12.php').content)
    arealist = web_content.split('arealist=')[1][2:-3]
    # decode arealist to stat_data
    all_stat_data = json.loads(urllib.parse.unquote(arealist))
    # city data
    taipei = City.objects.get(name = 'taipei')
    t_lat = taipei.l_lat
    t_lng = taipei.l_lng

    for stat_id, stat_data in all_stat_data.items():
        s_lat = Decimal(stat_data.get('lat', ''))
        s_lng = Decimal(stat_data.get('lng', ''))
        row = (t_lat - s_lat) // HEIGHT
        col = (s_lng - t_lng) // WIDTH
        name = stat_data.get('sna', '')
        # print (name, row, col)
        box = CityBox.objects.get(row = row, col = col)
        UbikeStat.objects.create(
            name = name, 
            lat = s_lat,
            lng = s_lng,
            box = box, 
            bemp = stat_data['bemp'],
            sbi = stat_data['sbi']
        )


def sync_ubikes_amount_func():
    # get arealist
    web_content = str(requests.get('http://taipei.youbike.com.tw/cht/f12.php').content)
    arealist = web_content.split('arealist=')[1][2:-3]
    # decode arealist to stat_data
    all_stat_data = json.loads(urllib.parse.unquote(arealist))
    # update sbi & bemp data
    try:
        for stat_id, stat_data in all_stat_data.items():
            print (stat_data.get('sna', 'no name'))
            stat = UbikeStat.objects.get(name = stat_data.get('sna', ''))
            stat.bemp = stat_data.get('bemp', 0)
            stat.sbi = stat_data.get('sbi', 0)
            stat.save()
    except Exception as e:
        print (e)
    finally:
        print ('update completed...')

def sync_ubikes_amount (request):
    scheduler = django_rq.get_scheduler('high')

    scheduler.schedule(
        scheduled_time = datetime.datetime.utcnow(),
        func = sync_ubikes_amount_func,
        interval = 10,
    )

def search_ubike_stat (request, city):
    # 0: OK
    success = {
        "code": 0,
        "result": []
    }

    # -1: invalid latitude or longitude
    invalid_data = {
        "code": -1,
        "result": []
    }

    # -2: given location not in Taipei City
    wrong_location = {
        "code": -2,
        "result": []
    }

    # -3: system error
    system_error = {
        "code": -3,
        "result": []
    }

    if request.method == 'GET':
        try:
            # get api city (/v1/ubike-station/{city}/?lat={lat}&lng={lng})
            city = City.objects.get(name = city)

            # get params
            lat = request.GET['lat']
            lng = request.GET['lng']
            
            # convert to Decimal
            current_lat = Decimal(lat)
            current_lng = Decimal(lng)

            # check location in Taipei or not
            google_geo_api = 'http://maps.googleapis.com/maps/api/geocode/json?address={},{}'.format(lat, lng)
            rep = requests.get(google_geo_api).json()
            if rep['status'] == "OK":
                city_name = rep['results'][-2]['address_components'][0]['short_name']
                if city_name != "Taipei City":
                    raise Exception('NotInTaipie')
            else:
                raise Exception('NotInTaipie')


            city_lat = city.l_lat
            city_lng = city.l_lng

            # find the current postition in which box
            row = (city_lat - current_lat) // HEIGHT
            col = (current_lng - city_lng) // WIDTH

            # box of current postition
            center_box = CityBox.objects.get(row = row, col = col)

            stations = []
            iter_num = 1
            row = int(row)
            col = int(col)

            # find 2 the nearest ubike stations
            while (len(stations) < 5):
                row_range = list(range(row - iter_num, row + iter_num + 1))
                col_range = list(range(col - iter_num, col + iter_num + 1))
                boxes = CityBox.objects.filter(row__in = row_range, col__in = col_range)
                stations = list(boxes.exclude(ubikestat__isnull = True).values('ubikestat__name', 'ubikestat__sbi', 'ubikestat__lat', 'ubikestat__lng'))
                iter_num += 1

            result = heapq.nsmallest(2, stations, key = lambda x: (current_lat - x['ubikestat__lat'])**2 + (current_lng - x['ubikestat__lng'])**2)
            success['result'] = [{'name': x['ubikestat__name'], 'num_ubike': x['ubikestat__sbi']} for x in result]

            return_obj = success

        except ValueError:
            logger.error('ValueError')
            return_obj = invalid_data

        except KeyError:
            logger.error('KeyError')
            return_obj = invalid_data

        except ObjectDoesNotExist:
            logger.error('ObjectDoesNotExist')
            return_obj = system_error

        except Exception as e:
            if e.args[0] == "NotInTaipie":
                logger.error('location not in Taipei')
                return_obj = wrong_location
            elif str(e) == "[<class 'decimal.ConversionSyntax'>]":
                logger.error('decimal.ConversionSyntax')
                return_obj = invalid_data
            else:
                logger.error(str(e))
                return_obj = system_error

        except:
            return_obj = system_error
        
    else:
        # system error
        return_obj = system_error
    
    return JsonResponse(return_obj)

