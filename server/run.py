# Purpose of run.py file
#----------"Intiatie to launch the APP"---------------
#----------"Starts Gunicorn server from -------------
import sys

#(Adding "APP" directory path to file for importing functions from app/__init__.py & config.py)
sys.path.append('../') 
from app import create_app
#from app.config import DevConfig, ProdConfig, configs

#(Importing logger attribute from server/logs.py file)
from logs import setup_logging,logger

#(Importing python module logging for log purpose)
import logging


def init_app(env, **kwargs):
    try:
      setup_logging('INFO')
      if env == '':
         raise TypeError('Supplied Env value is empty') # (Checks, if we are passing the env value as empty and raises exception)
      logger.info('Starting APP in {} mode'.format(env))
      return create_app()
    except ValueError as e:
      logger.error('Gunicorn server failed to start due to ValueError.{}'.format(e))
    except Exception as e:
      logger.error('Gunicorn server failed to start. {}'.format(e))

