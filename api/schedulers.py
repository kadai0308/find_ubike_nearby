from api.models import City, CityBox, UbikeStat
import django_rq
import requests
import json
import urllib
import datatime

scheduler = django_rq.get_scheduler('default')

scheduler.schedule(
    scheduled_time = datetime.utcnow(),
    func = sync_ubikes_amount,
    interval = 20,
)


def sync_ubikes_amount ():
    # get arealist
    web_content = str(requests.get('http://taipei.youbike.com.tw/cht/f12.php').content)
    arealist = web_content.split('arealist=')[1][2:-3]
    # decode arealist to stat_data
    all_stat_data = json.loads(urllib.parse.unquote(arealist))
    # update sbi & bemp data
    try:
        for stat_id, stat_data in all_stat_data.items():
            stat = UbikeStat.objects.get(name = stat_data.get('sna', ''))
            stat.bemp = stat_data.get('bemp', 0)
            stat.sbi = stat_data.get('sbi', 0)
            stat.save()
    except Exception as e:
        print (e)
    finally:
        print ('update completed...')
