# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """    
    dids = db().select(db.dids.ALL, orderby=~db.dids.date_created)
    for d in dids:
        d.body = db(db.elements.did_id==d.id).select(orderby=db.elements.stack_num)
    return dict(dids=dids)


@auth.requires_login()
def create_did():

    data = json.loads(request.vars['data'])
    author = auth.user_id
    date_created = datetime.datetime.utcnow()

    did_id = db.dids.insert(author_id = author,
                            date_created = date_created,
                            title = data['title'],
                            likes = 0,
                            spam = 0,
                            link = None)

    did = DIV(P('Author: '+str(author)),
              P('Posted: '+str(date_created)),
              P('Title: '+str(data['title'])))
                            
    elem_count = 0
    for b in data['body']:
        db.elements.insert(did_id = did_id,
                       stack_num = elem_count,
                       is_image = b['image'],
                       element_data = b['value'])
        if (b['image']): did.append(P('ITS AN IMAGE OMG'))
        did.append(P( 'Body' + str(elem_count) + ': ' + b['value']))
        elem_count += 1

    return did

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


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


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
