# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import logging, urlfetch
import datetime
logger = logging.getLogger("web2py.app.myweb2pyapplication")
logger.setLevel(logging.DEBUG)

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to Spentime App!")
    return dict(message=T(''))

@auth.requires_login()
def timeline():
    timeline_table = db(db.timeline.user_extra_id==auth.user_id).select()
    hours=None
    if len(timeline_table) and timeline_table[-2]['end_time']:
        start_time = datetime.datetime.strptime(timeline_table[0]['start_time'],"%Y-%m-%dT%H:%M:%S.%f")
        end_time = datetime.datetime.strptime(timeline_table[-2]['end_time'],"%Y-%m-%dT%H:%M:%S.%f")
        hours = (end_time - start_time).seconds//3600
        # mail.send('sergiykhalimon@gmail.com',
        # subject='h',
        # message='heee')
    return dict(hours=hours)

def user():
    def get_uid():
        pass
    # user_id = auth.user_id
    social = False
    if request.args(0)=='profile':
        social=True
        record = auth.user_id or redirect(URL('index'))
        form = SQLFORM(db.auth_user, record)
        if form.process().accepted:
            response.flash = T('Records updated')
        grid = SQLFORM.smartgrid(db.timeline,
                                 user_signature=False,
                                 searchable=False,
                                 csv=False)
    else:
        form = auth()
    if request.args(0) == 'vk':
        account = VkAccount()
        # token = account.
        db.user_extra.insert(auth_id=auth.user_id, token=token)
        # logger.debug(account.accessToken())
        redirect(URL('user', args='profile'))
    if request.args(0) == 'facebook':
        pass

    if request.args(0) == 'register':                              # for disable selected fields
        for field in ['vk_uid', 'fb_uid']:
            db.auth_user[field].readable = db.auth_user[field].writable = False

    return locals()

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
