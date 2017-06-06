from __future__ import unicode_literals
import multiprocessing
import gunicorn.app.base
from gunicorn.six import iteritems
import sys
sys.path.append('../')
from app import create_app
from logs import logger,setup_logging

def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self,app,options=None):
        self.options = options or {}
        self.application = app
        setup_logging('INFO')
        super(StandaloneApplication,self).__init__()

    def load_config(self):
        logger.info("Loading Gunicorn configuration file")
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        logger.info('Starting APP in PROD mode')
        return self.application 


if __name__ == '__main__':
    options = {
        'bind': '%s:%s' % ('127.0.0.1', '5000'),
        'workers': 1,
         'worker_class':'egg:meinheld#gunicorn_worker',
	'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({X-Real-IP}i)s" %(L)s',
         'accesslog': '../logs/access.log',
         'errorlog': '../logs/server.log',
         'timeout': 1400
    }
    StandaloneApplication(create_app,options).run()
