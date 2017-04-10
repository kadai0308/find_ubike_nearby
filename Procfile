web: gunicorn find_ubike_nearby.wsgi server.log
worker: python manage.py rqworker high default low
clock: rqscheduler -u $REDISTOGO_URL -i 10