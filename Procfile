web: gunicorn find_ubike_nearby.wsgi server.log
worker.1: python manage.py rqworker high default low
worker.2: rqscheduler -i 2