import json
import falcon
from server.logs import logger

class RootResources(object):
    def on_get(self, req, resp):
        logger.info("Executing the RootResource class")
        resp.body = json.dumps({
            'message': 'Hello, World!',
        })
        resp.status = falcon.HTTP_200


class RootNameResources(object):
    def on_post(self, req, resp, name):
        logger.info("Executing the RootNameResource class")
        resp.body = json.dumps({
            'message': 'Hello, {}!'.format(name)
        })
        resp.status = falcon.HTTP_200

