import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
#from html.parser import HTMLParser
import folium
from IPython.display import display,HTML
#from BoundingBox import *
from app.models.what_if.BoundingBox import BoundingBox

#SF_COORDINATES = (float(lat),float(lng))
#blr = folium.Map(location=SF_COORDINATES, zoom_start=16,control_scale=True)


class TwitterListener(StreamListener):
	# lat = 0.0
	# lng = 0.0
	# radius = 5
	'''consumer_key = "KZMUN3xQHFm9NhvHhksX8i6CD"
	consumer_secret = "L6rYJZ35iVPaCii8PbPO3QheuRjqwOhEYcY0EvmABkssc9KSVB"
	access_token = "389300897-nVWVS1ZE32YN1gSINeOxIyK4iDaY46mffI2owo4Z"
	access_secret = "HKXOKf6yoGv3mZeTvPqgMcxxSGawfvIBvUHn6pjeQp18t"
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_secret) '''


	# def __init__(self,lat,lng,radius):
	# 	self.lat = float(lat)
	# 	self.lng = float(lng)
	# 	self.radius = int(radius)

	def getAuthentication(self):
		consumer_key = "KZMUN3xQHFm9NhvHhksX8i6CD"
		consumer_secret = "L6rYJZ35iVPaCii8PbPO3QheuRjqwOhEYcY0EvmABkssc9KSVB"
		access_token = "389300897-nVWVS1ZE32YN1gSINeOxIyK4iDaY46mffI2owo4Z"
		access_secret = "HKXOKf6yoGv3mZeTvPqgMcxxSGawfvIBvUHn6pjeQp18t"
		auth = OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_secret)
		#api = tweepy.API(auth)
		return auth


	def on_status(self, status):
		print(status.text)
		if status.coordinates:
			print('coordinates', status.coordinates)
		if status.place:
			print('place:', status.place.full_name)
		return True

	def on_error(self, status):
		print(status)
		return True

	def getTwitterStream(self,lat,lng,radius):
		box = BoundingBox(lat, lng)
		box1 = box.get_bounding_box_lat_long(5)
		twitter_stream = Stream(self.getAuthentication(), TwitterListener())
		twitter_stream.filter(locations=[box1.lon_min, box1.lat_min, box1.lon_max, box1.lat_max])
		return twitter_stream


def main():
	tweet = TwitterListener()
	tweet.getTwitterStream()

if __name__ == "__main__":
    main()
