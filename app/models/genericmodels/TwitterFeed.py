import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import json
import psycopg2
from time import *
import random


class TwitterFeed(StreamListener):
    def on_data(self, data):
        all_data = json.loads(data)

        jaipurDict = {"26.892652": "75.814625", "26.894145": "75.814625", "26.894145": "75.812973",
                      "26.892652": "75.812973", "26.856067": "75.806349", "26.856529": "75.806349",
                      "26.856529": "75.805689", "26.856067": "75.805689", "26.909801": "75.82073"}
        jaipurlat = ['26.892652', '26.894145', '26.856067', '26.856529', '26.909801']

        if all_data.get('coordinates', None) is not None and all_data.get('retweet') != 'false':
            conn = psycopg2.connect(host="52.55.107.13", dbname="atlantisdb", user="sysadmin", password="sysadmin")
            #testConn = psycopg2.connect(host="34.201.61.177", dbname="atlantisdb", user="sysadmin", password="sysadmin")
            # conn = psycopg2.connect(host="54.197.22.58", dbname="atlantisdb", user="sysadmin" , password="traV-ruc6eza")
            mark = conn.cursor()
            #testMark = testConn()
            tweet = all_data['text']
            userName = all_data['user']['screen_name']
            # latitude = all_data['coordinates']['coordinates'][1]
            # longitude = all_data['coordinates']['coordinates'][0]
            latitude = random.choice(jaipurlat)
            longitude = jaipurDict[latitude]
            created_at = all_data['timestamp_ms']
            fullName = all_data['place']['full_name']
            print(latitude, longitude, tweet)
            mark.execute(
                "INSERT INTO twitter_stream (tweet_user, tweet_text, latitude, longitude , postedon) VALUES (%s, %s, %s, %s, %s)",
                (userName.encode('utf-8'), tweet.encode('utf-8'), latitude, longitude, created_at))
            #testMark.execute("INSERT INTO twitter_stream (tweet_user, tweet_text, latitude, longitude , postedon) VALUES (%s, %s, %s, %s, %s)",(userName.encode('utf-8'), tweet.encode('utf-8'), latitude, longitude, created_at))
            conn.commit()
            mark.close()
            conn.close()
        return (True)

    def on_error(self, status):
        print("error getting connection : ", status)

    # return(True)

    def on_timeout(self):
        print('Timeout')
        return (True)

    def getauthentication(self):
        consumer_key = "KZMUN3xQHFm9NhvHhksX8i6CD"
        consumer_secret = "L6rYJZ35iVPaCii8PbPO3QheuRjqwOhEYcY0EvmABkssc9KSVB"
        access_token = "389300897-nVWVS1ZE32YN1gSINeOxIyK4iDaY46mffI2owo4Z"
        access_secret = "HKXOKf6yoGv3mZeTvPqgMcxxSGawfvIBvUHn6pjeQp18t"
        try:
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_secret)
        except:
            print('Error: Authentication Failed')
        return auth

    def getStream(self):
        tStream = tweepy.Stream(self.getauthentication(), TwitterFeed())
        tFeed = tStream.filter(track=['accident', 'fire', 'killing', 'bomb', 'attack', 'stabbing'])


def main():
    api = TwitterFeed()
    api.getStream()


if __name__ == '__main__':
    main()
