# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    # db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
    db = DAL('postgres://postgres:postgres@localhost/spendtime')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

# from gluon.contrib.login_methods import lo

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

auth.settings.extra_fields['auth_user']= [
  Field('vk_uid', 'integer', unique=False, required=False),
  Field('fb_uid', 'integer', unique=False, required=False)]

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## add table for save social data
db.define_table('user_extra',
                Field('auth_id', 'reference auth_user'),
                Field('social_type', 'string'),
                Field('token', 'string'),
                format='%(auth_id)s_%(social_type)s')

db.define_table('timeline',
                Field('user_extra_id', 'reference user_extra'),
                Field('week_day', 'string'),
                Field('start_time', 'string'),
                Field('end_time', 'string'))

## configure email
from gluon.tools import Mail
mail = Mail()
mail = Mail('smtp.mail.ru:587', 'semyonx@mail.ru', 'semyonx:schambala2012')

# mail = auth.settings.mailer
# mail.settings.server = 'logging' or 'smtp.mail.ru:587'
# mail.settings.sender = 'semyonx@mail.ru'
# mail.settings.login = 'semyonx:schambala2012'  ##############CHANGE THOSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
# from gluon.contrib.login_methods.rpx_account import use_janrain
# use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

## Define oauth application id and secret.
FB_CLIENT_ID='681470318582361'
FB_CLIENT_SECRET="cb5b80069e23cee1ea085ad6be1cd159"
VK_CLIENT_ID='4254824'
VK_CLIENT_SECRET="75qxexahQqnAWTgjxqF6"
VK_REDIRECT_URI=FB_REDIRECT_URI="http://localhost.org:8000/spendtime/default/user/profile"


## import required modules
try:
    import json
except ImportError:
    from gluon.contrib import simplejson as json
# from facebook import GraphAPI, GraphAPIError
from gluon.contrib.login_methods.oauth20_account import OAuthAccount

## extend the OAUthAccount class
class FbAccount(OAuthAccount):
    """OAuth impl for FaceBook"""
    AUTH_URL="https://graph.facebook.com/oauth/authorize"
    TOKEN_URL="https://graph.facebook.com/oauth/access_token"

    def __init__(self):
        OAuthAccount.__init__(self, None, FB_CLIENT_ID, FB_CLIENT_SECRET,
                              self.AUTH_URL, self.TOKEN_URL,
                              scope='email',
                              state="auth_provider=facebook",)
                              # display='popup')
        self.graph = None

    def get_user(self):
        '''Returns the user using the Graph API.
        '''
        if not self.accessToken:
            return None

        # if not self.graph:
        #     self.graph = GraphAPI((self.accessToken()))

        user = None
        # try:
        #     user = self.graph.get_object("me")
        # except GraphAPIError, e:
        #     session.token = None
        #     self.graph = None

        if user:
            if not user.has_key('username'):
                username = user['id']
            else:
                username = user['username']

            if not user.has_key('email'):
                email = '%s.fakemail' %(user['id'])
            else:
                email = user['email']

            return dict(first_name = user['first_name'],
                        last_name = user['last_name'],
                        username = username,
                        email = '%s' %(email) )

class VkAccount(OAuthAccount):
    """OAuth impl for FaceBook"""
    AUTH_URL="http://oauth.vk.com/authorize"
    TOKEN_URL="https://oauth.vk.com/access_token"

    def __init__(self):
        OAuthAccount.__init__(self, None, VK_CLIENT_ID, VK_CLIENT_SECRET,
                              self.AUTH_URL, self.TOKEN_URL,
                              scope='offline',
                              response_type='code',
                              # state="auth_provider=vk",
        )
        self.graph = None
    def get_user(self):
        '''Returns the user using the Graph API.
        '''
        if not self.accessToken:
            return None

        # if not self.graph:
        #     self.graph = GraphAPI((self.accessToken()))

        user = None
        # try:
        #     user = self.graph.get_object("me")
        # except GraphAPIError, e:
        #     session.token = None
        #     self.graph = None

        if user:
            if not user.has_key('username'):
                username = user['id']
            else:
                username = user['username']

            if not user.has_key('email'):
                email = '%s.fakemail' %(user['id'])
            else:
                email = user['email']

            return dict(first_name = user['first_name'],
                        last_name = user['last_name'],
                        username = username,
                        email = '%s' %(email) )
## use the above class to build a new login form
# auth.settings.login_form=VkAccount()

import logging
logger = logging.getLogger("web2py.app.spendtime")
logger.setLevel(logging.DEBUG)