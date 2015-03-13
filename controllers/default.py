# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

import logging


@auth.requires_login()
def index():

    """
    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
    
    if request.args and request.args[0] == 'top':
        dids = db().select(db.dids.ALL, orderby=~db.dids.date_created)
    elif request.args and request.args[0] == 'explore':
        xauthors = set([row.following_id for row in db(db.followers.follower_id.belongs(following)).select(db.followers.following_id)])
        authors = xauthors - following - set([str(auth.user_id)])
        dids = db(db.dids.author_id.belongs(authors)).select(orderby=~db.dids.date_created)
    elif request.args and request.args[0] == 'followers':
        authors = [row.follower_id for row in db(db.followers.following_id == auth.user_id).select(db.followers.follower_id)]
        dids = db(db.dids.author_id.belongs(authors)).select(orderby=~db.dids.date_created)        
    else:
        authors = following | set(str(auth.user_id))
        dids = db(db.dids.author_id.belongs(authors)).select(orderby=~db.dids.date_created)

    for d in dids:
        d.body = db(db.elements.did_id==d.id).select(orderby=db.elements.stack_num)
        d.comments = db(db.comments.did_id==d.id).select(orderby=~db.comments.date_created)
        d.following = (str(d.author_id) in following)
        d.like = (db.likes(user_id = auth.user_id, did_id = d.id) != None)
    return dict(dids=dids)


@auth.requires_login()
def create_did():
    """
    creates a new did based on form data uploaded via ajax
    """
    data = request.vars
    author = auth.user_id 
    date_created = datetime.datetime.utcnow()
    
    did_id = db.dids.insert(author_id = author,
                            date_created = date_created,
                            title = data['did_title'],
                            likes = 0,
                            spam = 0,
                            link = None)
    
    did = DIV(H4(data['did_title']),
              _style="width:100%")
    
    if len(data) == 1:
        did.append(P('posted by: '+str(db.auth_user(author).email) +' on '+ str(date_created)))
        did.append(HR( _class="did-sep"))
        did.append(A('comment', _id="com_btn"+str(did_id), _class="btn form-btn", _onclick="addComment('new"+str(i)+"', "+str(did_id)+", this)"))
        return did
    
    num_elems = (len(data) - 2)/2
    for i in range(0, num_elems):
        d = data['elem'+str(i)]
        if (data['is_img' + str(i)] == 'True'):
            img_id = db.image.insert(img = db.image.img.store(d.file, d.filename))
            db.elements.insert(did_id = did_id,
                stack_num = i,
                is_image = True,
                element_data = img_id)
            did.append(IMG( _style="witdh:100%", _src=URL('download', args = db.image(img_id).img )))
        else:
            db.elements.insert(did_id = did_id,
                stack_num = i,
                is_image = False,
                element_data = str(d))
            did.append(P(XML(str(d).replace('\n','<br />')), _style="word-break: break-word"))
            
    did.append(P('posted by: '+str(db.auth_user(author).email) +' on '+ str(date_created)))

    bottom = DIV( _class="clear")

    bottom.append(HR( _class="did-sep"))
    bottom.append(A('comment', _id="com_btn"+str(did_id), _style="float:right", _class="btn form-btn", _onclick="addComment('"+data['div_id']+"', "+str(did_id)+", this)"))
    bottom.append(DIV( _id="com_"+data['div_id'] ))

    did.append(bottom)
    
    return did
    

"""###################################################################################################
###########
########### profile
###########
###################################################################################################"""

@auth.requires_login()
def update_profile():
    data = request.vars
    user_id = auth.user.id
    logging.error('in update_profile')
    #logging.error(data)
    # if an updated about in vars update user's about 
    #logging.error(data)
    about_str = ''
    if(data['about']):

        #logging.error('updating about\n')
        logging.error(linkify(data['about']))
        db(db.users.user_id == user_id).update(about=str(data['about']))
        #logging.error('updated about\n')
    else:
        logging.error('inserting an image')
        db(db.users.user_id == user_id).update(profile_img=data['image'])
        logging.error('inserted an image')
    return 

@auth.requires_login()
def profile():
    user = db(db.users.user_id == auth.user.id).select().first()
    name = request.args(0)
    if name:
        
        test = db(db.users.username == name).select().first() 
        logging.error('requested ' + name + "'s profile" )
        if test != None:
            user = test
        else:
            redirect(URL('default', 'profile/' + user.username))
    else:
        redirect(URL('default', 'profile/' + user.username))

    
    about_str = linkify(user.about).decode('unicode-escape')
    dids = db(db.dids.author_id == user.user_id).select(orderby=~db.dids.date_created)
    for d in dids:
        d.body = db(db.elements.did_id==d.id).select(orderby=db.elements.stack_num)
        d.comments = db(db.comments.did_id==d.id).select(orderby=~db.comments.date_created)
    return dict(dids=dids, user=user, about_str=about_str)



"""################################################################################################"""


@auth.requires_login()
def add_comment():
    data = request.vars
    
    db.comments.insert(did_id = data['did_id'],
                       date_created = datetime.datetime.utcnow(),
                       author_id = auth.user_id,
                       reply_id = None,
                       body = data['comment'])
    
    comment = DIV( B(str(auth.user.first_name + ' ' + str(auth.user.last_name)))+ ' ' + P(XML(data['comment'].replace('\n','<br />')), _style="word-break: break-word"),
                   _class="comment" )
    
    return comment
    
"""
follow() called via AJAX adds an entry to the followers table
"""
def follow():
    data = request.vars
    
    if not db.followers(following_id = data['following_id'], follower_id = auth.user_id):
        db.followers.insert(following_id = data['following_id'],
                            follower_id = auth.user_id)
    
    return
    
"""
unfollow() called via AJAX deletes entry from the followers table
"""
def unfollow():
    data = request.vars

    f = db.followers(following_id = data['following_id'], follower_id = auth.user_id)
    if f:
        db(db.followers.id==f.id).delete()
    return
    
def like():
    data = request.vars
    if not db.likes(did_id = data['did_id'], user_id = auth.user_id):
        db.likes.insert(did_id = data['did_id'],
                            user_id = auth.user_id)
        
    return

def unlike():
    data = request.vars
          
    l = db.likes(did_id = data['did_id'], user_id = auth.user_id)
    if l:
        db(db.likes.id==l.id).delete()
        
    return


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
