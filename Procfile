web: gunicorn find_ubike_nearby.wsgi server.log
worker: python manage.py rqworker high default low
clock: python api/clock.py