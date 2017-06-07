import json
import falcon
from server.logs import logger
from app.models.wastemanagement.wasteCollectionRoute import wasteCollectionRoute

class wasteBinCollectionRoute:
    def on_get(self, req, resp):
      try:
        wasteBin = wasteCollectionRoute()
        #input_json = wasteBin.dataProcessingFromSampleFiles("ferrovial_vehicle.csv", "ferrovial_pickups.csv", 75)
        input_json=wasteBin.dataProcessingFromCDP()
        result_json = wasteBin.model(input_json)
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result_json)
      except FileNotFoundError as e:
        logger.error('WasteBin Collection ended with error.{}'.format(e))
        resp.status = falcon.HTTP_404
        resp.body= json.dumps({"Status Code":404,"Description":"Not found","title":"WasteBinCollection"})
        #raise falcon.HTTPError(status="404 Not found",title='WasteBin Predictions',description='Not Found',code='404')
      except KeyError as e:
        logger.error('WasteBin Collections ended with exception.{}'.format(e))
        resp.status = falcon.HTTP_400
        resp.body= json.dumps({"Status Code":400,"Description":"Malformed Request","title":"WasteBinCollection"})
        #raise falcon.HTTPError(status="400 Bad Request",title='WasteBin Predictions',description='Invalid Request',code=400)
      except Exception as e:
        logger.error('WasteBin Collections ended with exception.{}'.format(e))
        resp.status = falcon.HTTP_500
        resp.body= json.dumps({"Status Code":500,"Description":"Internal Server Error","title":"WasteBinCollection"})
        #raise falcon.HTTPError(status="500 Internal Server Error",title='WasteBin Predictions',description='Internal Server Error',code=500)
      
