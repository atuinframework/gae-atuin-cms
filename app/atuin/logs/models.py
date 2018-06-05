# -*- coding: utf-8 -*-
from google.appengine.ext import ndb


class Log(ndb.Model):
    timestamp = ndb.DateTimeProperty('ts', auto_now_add=True, indexed=True)

    event_type = ndb.StringProperty('ty', required=True, indexed=True)
    event_title = ndb.StringProperty('ti')
    event_data = ndb.TextProperty('d')

    @classmethod
    def log_event(cls, ev_type, ev_title, ev_data=''):
        l = cls()
        l.event_type = ev_type
        l.event_title = ev_title
        l.event_data = ev_data

        l.put()
