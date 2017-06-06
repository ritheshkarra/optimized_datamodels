#!/usr/bin/python

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
 
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
 
 
 
class Component(ApplicationSession):
   """
   An application component that publishes an event every second.
   """
 
   def __init__(self, realm = "realm1"):
      ApplicationSession.__init__(self)
      self._realm = realm
 
 
   def onConnect(self):
      self.join(self._realm)
 
 
   @inlineCallbacks
   def onJoin(self, details):
      counter = 0
      while True:
         self.publish('com.myapp.topic1', counter)
         counter += 1
         yield sleep(1)