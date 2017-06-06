#Purpose for file
#------------Launching APP on server--------------
#------------Adds routing mechanism to the end responder---------
import logging
import falcon
#from app.config import DevConfig, ProdConfig, configs
from app.middleware import Crossdomain, AuthMiddleware, JSONTranslator
from app.models import RootResources, RootNameResources
from app.models.parking.endpoints import ParkingPredictions,NextPSpace,DynamicParkingBasedOnSurrounding,CompParking
from app.models.environment.endpoints import So2Predictions,HumidityPredictions,AmbientTempPredictions
from app.models.toxic_heavy_gas_dispersion.endpoints import Weather,airDispersion
from app.models.light.endpoints import lightIntensity
from app.models.wastemanagement.endpoints import wasteBinCollectionRoute
from app.models.genericmodels.endpoints import NearByTraffic, NearPlaces, NearByMap
#from server.logs import logger #importing logger object from server/logs.py file

def create_app():  #Create app function instantiates API object and setup API routes
   try:
      app = falcon.API(middleware=[Crossdomain(),
          # AuthMiddleware(),
          JSONTranslator()])    ## Create Falcon API object through which we can add routes
      logger.info('APP started successfully')
      setup_routes(app) #Adding routes to falcon API
      logger.info(' Routes enabled on APP')
   except RuntimeError as e:
      logger.error('Launching APP failed {}'.format(e))
      raise falcon.HTTPError(status="503 APP Unavailable",title='Atlantis APP',description='Atlantis falcon APP failed to start',code=503)
   except Exception as e:
      logger.error('Error at create_app function'.format(e))
#   isinstance(app,"falcon.api.API")
   return app

def setup_routes(app): 
      """ It used to create routes and responds to the responder using WSGI.
       Here, we create the routes and call the respective endpoints available on /app/models directory  
      """
      app.add_route('/', RootResources()) 
      app.add_route('/{name}', RootNameResources())
      app.add_route('/parking/spacepredictions', ParkingPredictions())
      app.add_route('/parking/nextparkingspace', NextPSpace())
      app.add_route('/parking/surrounding', DynamicParkingBasedOnSurrounding())
      app.add_route('/airquality/so2',So2Predictions())
      app.add_route('/airquality/humidity', HumidityPredictions())
      app.add_route('/airquality/ambienttemp',AmbientTempPredictions())
      app.add_route('/gas/weather', Weather())
      app.add_route('/gas/airdispersion', airDispersion())
      app.add_route('/light/intensity', lightIntensity())
      app.add_route('/waste/binroute', wasteBinCollectionRoute())
      app.add_route('/parking/all', CompParking())
      app.add_route('/crisis/nearbyplace', NearPlaces())
      app.add_route('/crisis/nearbytraffic', NearByTraffic())
      app.add_route('/crisis/nearbymap', NearByMap())
