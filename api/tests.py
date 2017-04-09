from django.test import TestCase
from api.models import City, CityBox, UbikeStat

import urllib
from decimal import *
import json
import requests

class TestApi(TestCase):

    def setUp (self):
        _setup_city('taipei')
        _setup_citybox(20, 20, 'taipei')
        _setup_ubike_stat()

    def test_api_stat_success (self):
        # code: 0
        response = self.client.get('/v1/ubike-station/taipei/?lat=25.041332&lng=121.555838').json()
        assert response['code'] == 0

    def test_api_stat_invaild_data (self):
        # code: -1
        response = self.client.get('/v1/ubike-station/taipei/?lat=25.041332&lng=XDDDDD').json()
        assert response['code'] == -1

    def test_api_stat_not_in_taipei (self):
        # code: -2
        response = self.client.get('/v1/ubike-station/taipei/?lat=25.037925&lng=121.314757').json()
        assert response['code'] == -2


# private
def _setup_city (city_name):
    City.objects.create(
        name = city_name,
        l_lat = Decimal('25.210380'),
        l_lng = Decimal('121.457156'),
        r_lat = Decimal('24.959974'),
        r_lng = Decimal('121.665821')
    )

def _setup_citybox (width, height, city_name):
    city = City.objects.get(name = city_name)
    for i in range(width):
        for j in range(height):
            CityBox.objects.create(row = i, col = j, city = city)

def _setup_ubike_stat ():
    WIDTH = Decimal('0.0104332')
    HEIGHT = Decimal('0.0125203')
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
        UbikeStat.objects.create(name = name, lat = s_lat, lng = s_lng, box = box, bemp = stat_data['bemp'], sbi = stat_data['sbi'])

