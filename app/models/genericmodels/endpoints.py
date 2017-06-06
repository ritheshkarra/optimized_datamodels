import pandas as pd
import falcon
import json

from app.models.genericmodels.TwitterFeed import TwitterFeed
from app.models.genericmodels.NearByPlaces import NearByPlaces
from app.models.genericmodels.criss_mangment import CrisisManagement


class NearByTraffic(object):
    def on_get(self, req, resp):
        input_params = req.params
        latitude = input_params['latitude']
        longitute = input_params['longitute']
        # radius = input_params['radius']

        cm = CrisisManagement()
        traffic = cm.cong_source(str(latitude), str(longitute), 200)
        #nearBy = NearByPlaces(latitude, longitute)
        #traffic = nearBy.nearby_traffic()

        resp.status = falcon.HTTP_200
        resp.body = pd.DataFrame(traffic).to_json(orient='records')


class NearByMap(object):
    def on_get(self, req, resp):
        input_params = req.params
        latitude = input_params['latitude']
        longitute = input_params['longitute']
        kword = input_params['keyword']
        rad = input_params['radius']

        cm = CrisisManagement()
        result = cm.nearby(str(latitude), str(longitute), radius=str(rad), keyword=str(kword))

        result = pd.DataFrame(result)
        mapResult = cm.nearby_map(result,str(latitude), str(longitute))
        mapResult.save('map.html')
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        with open('map.html', 'r') as f:
            resp.body = f.read()


class NearPlaces(object):
    def on_get(self, req, resp):
        input_params = req.params
        latitude = input_params['latitude']
        longitute = input_params['longitute']
        kword = input_params['keyword']
        rad = input_params['radius']
        cm = CrisisManagement()
        result = cm.nearby(str(latitude), str(longitute), radius=str(rad), keyword=str(kword))
        #nearBy = NearByPlaces(latitude, longitute)
        #result = nearBy.nearby(rad, kword)
        resultDF = pd.DataFrame(result)

        resp.status = falcon.HTTP_200
        # resp.content_type = 'text/html'
        resp.body = resultDF.to_json(orient='records')


class TwitterStream(object):
    def on_get(self, req, resp):
        stream = TwitterFeed()
        stream.getStream()
