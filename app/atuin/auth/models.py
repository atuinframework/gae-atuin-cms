# -*- coding: utf-8 -*-
import datetime
import random
import hashlib
import collections

from passlib.hash import sha256_crypt
from flask_babel import lazy_gettext
from atuin.mailing import send_mail

from google.appengine.ext import ndb, blobstore
from google.appengine.api import images as gapi_images
from atuin.utils import update_searchable_set
from permission_policies import user_role_polices, role_policy_functions


class User(ndb.Model):
    role = ndb.StringProperty('r', required=True, default='GUEST')
    active = ndb.BooleanProperty('a', default=False)
    auth_ids = ndb.StringProperty('ai', repeated=True)

    email = ndb.StringProperty('em', indexed=True, default='')
    username = ndb.StringProperty('un', required=True, indexed=True, default='')
    password = ndb.StringProperty('pwd', indexed=False)

    prefix = ndb.StringProperty('px', indexed=False, default='')
    name = ndb.StringProperty('n', indexed=True, default='')
    surname = ndb.StringProperty('s', indexed=True, default='')
    birthday = ndb.DateProperty('b')
    gender = ndb.StringProperty('g')
    address_city = ndb.StringProperty('ac')
    address_zip = ndb.StringProperty('az')
    address_country = ndb.StringProperty('ac')

    logo_image = ndb.BlobKeyProperty('li', indexed=False)
    logo_image_url = ndb.StringProperty('liu', indexed=False)

    preferences = ndb.PickleProperty('p')
    notes = ndb.StringProperty(indexed=False)

    otp = ndb.StringProperty('o', default='', indexed=True)
    otp_expire = ndb.DateTimeProperty('o_e', auto_now_add=True, indexed=False)

    name_searchable = ndb.StringProperty('ns', repeated=True)

    ins_timestamp = ndb.DateTimeProperty('i_ts', auto_now_add=True, indexed=False)
    upd_timestamp = ndb.DateTimeProperty('u_ts', auto_now=True, indexed=False)

    active_until = ndb.DateTimeProperty('au', default=None)
    last_login = ndb.DateTimeProperty('ll', default=None)

    def __repr__(self):
        return "<User %s %s role=%s>" % (self.key, self.username, self.role)

    def get_id(self):
        return self.key.id()

    def get_urlsafe(self):
        return self.key.urlsafe()

    @classmethod
    def get_by_key(cls, k):
        return ndb.Key(urlsafe=k).get()

    @classmethod
    def get_by_otp(cls, otp):
        otp = otp.strip()
        if otp:
            c = cls.query(cls.otp == otp).get()
            if c:
                if datetime.datetime.now() < c.otp_expire:
                    return c

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def age(self):
        try:
            age = (datetime.date.today() - self.birthday).days / 365.2425
        except:
            age = 0
        return int(age)

    def set_password(self, password):
        pwd = sha256_crypt.encrypt(password)
        self.password = pwd

    def check_password(self, password):
        if sha256_crypt.verify(password, self.password):
            # login ok
            return True

        return False

    @classmethod
    def check_otp(cls, otp):
        user = cls.query.filter(cls.otp_expire > datetime.datetime.now(), cls.otp == otp).first()
        if user:
            # invalidate it
            user.otp_expire = datetime.datetime.now()

        return user

    def generate_otp(self):
        otp = hashlib.sha256(str(random.randint(99999, 999999))).hexdigest()
        self.otp = otp
        self.otp_expire = datetime.datetime.now() + datetime.timedelta(hours=24)

        return otp

    def send_email(self, subject, message):
        res = send_mail(subject, message, [
            {'email': self.email},
        ])
        return res

    @property
    def role_title(self):
        return user_role_polices.get(self.role).get('title')

    @property
    def role_description(self):
        return user_role_polices.get(self.role).get('description')

    @property
    def role_functions(self):
        functions = []
        if self.role == 'ADMIN':
            for f in role_policy_functions.itervalues():
                functions += f
        else:
            for p in user_role_polices.get(self.role).get('policies'):
                functions += role_policy_functions.get(p)
        return list(set(functions))

    def has_function(self, func):
        if self.role == 'ADMIN':
            return True
        return func in self.role_functions

    def _pre_put_hook(self):
        ns = set()
        ns = update_searchable_set(ns, self.name)
        ns = update_searchable_set(ns, self.surname)
        ns.add(self.username)

        self.name_searchable = list(ns)

    @property
    def prefix_descr(self):
        return self.prefixes_d.get(self.prefix, self.prefix)
