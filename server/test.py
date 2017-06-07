from __future__ import unicode_literals
import multiprocessing
import gunicorn.app.base
from gunicorn.six import iteritems
from logs import logger,setup_logging,accesslog,errorlog
import falcon
import sys
sys.path.append('../')
from app import create_app


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class AtlantisApplication(gunicorn.app.base.BaseApplication):

    def __init__(self,app,options):
        self.options=options or {}
        self.application = app
        super(AtlantisApplication,self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        try:
           setup_logging('INFO')
           logger.info('Starting APP in PROD mode')
           return create_app() #self.application 
        except Exception as e: 
           logger.error('Falcon APP not loaded.{}'.format(e))
           raise falcon.HTTPError(status="503 APP Unavailable",title='Atlantis APP',description='Atlantis falcon APP failed to start',code=503)

if __name__ == '__main__':
   global options
   options = {
        'bind': '%s:%s' % ('127.0.0.1', '5000'),
        'workers': 1,
        'worker_class':'egg:meinheld#gunicorn_worker',
        'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%({X-Real-IP}i)s" %(L)s',
        'accesslog': accesslog,
        'errorlog': errorlog,
        'timeout': 1400
        }
   AtlantisApplication(create_app,options).run()
