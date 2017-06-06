#This file used for setting the values for Gunicorn WSGI Server. It bind's the service to port 5000.
# How to run the service
# /usr/local/bin/gunicorn -c config.py run:"init_app(env='PROD')" 
bind = 'localhost:5000'
workers = 1
worker_class = 'egg:meinheld#gunicorn_worker'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({X-Real-IP}i)s" %(L)s'
accesslog = '../logs/access.log'
errorlog = '../logs/server.log'
timeout=1200
