#!/usr/bin/python

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
 
from autobahn.twisted.wamp import ApplicationSession
 
 
 
class Component(ApplicationSession):
   """
   An application component that subscribes and receives events,
   and stop after having received 5 events.
   """
 
   def onConnect(self):
      self.join("realm1")
 
 
   @inlineCallbacks
   def onJoin(self, details):
 
      self.received = 0
 
      def on_event(i):
         print("Got event: {}".format(i))
         self.received += 1
         if self.received > 5:
            self.leave()
 
      yield self.subscribe(on_event, 'com.myapp.topic1')
 
 
   def onLeave(self, details):
      self.disconnect()
 
 
   def onDisconnect(self):
      reactor.stop()