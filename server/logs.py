#Custom logging setup
import logging.config
from server.test import options #From Gunicorn config file importing errorlog and accesslog file location

logger = logging.getLogger('APP') #Creating a global variable for logging which can be used in all files

def setup_logging(level='INFO'):  #Performing INFO level logging. Can be modified
    if level is not None:
        fmt = '[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s'
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': fmt,
                    'datefmt': '%Y-%m-%d %H:%M:%S %z'
                }
            },
            'handlers': {                            
                'errorfile': {
                    'formatter': 'standard',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'maxBytes': 102400,
                    'backupCount': 3,
                    'filename': options[errorlog]
                },
               'accessfile': {
                    'formatter': 'standard',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'maxBytes': 102400,
                    'backupCount': 3,
                    'filename': options[accesslog]
                } 
            },
            'loggers': {
                '': {
                    'handlers': ['accessfile'],
                    'level': level,
                    'propagate': True
                },
                'gunicorn.error': {
                    'handlers': ['errorfile'],
                    'level': 'ERROR',
                    'propagate': True
                },
                'gunicorn.access': {
                    'handlers': ['accessfile'],
                    'level': level,
                    'propagate': True
                }
            }
        }

        logging.config.dictConfig(config)  #Passing the Config dictonary to the class dictConfig in /usr/lib/python3.5/logging.config file
