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
        dids = db().select(db.dids.ALL, orderby=~db.dids.likes)
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

    i = 0;
    ds = []
    for d in dids:
        ds.append(did2DOM(d, following, i))
        i += 1
        
    return dict(dids=ds)

    
def did2DOM(row, following, div_num):
    """ things I need to pass
    did db row
    following
    div_num
    """
    
    #create did
    did = DIV( _class="did clear", _id="d"+ str(div_num) )
    
    #attach author
    did.append(A(db.users(row.author_id).username, _href=URL('default','profile', args=[db.users(row.author_id).username]), _class="did-author"))
    
    # attach title
    if row.title != '':
        did.append(H4(row.title, _class="did-title"))
    
    # get elements
    elems = db(db.elements.did_id==row.id).select(orderby=db.elements.stack_num).render()
    for e in elems:
        if e.is_image:
            did.append(IMG( _style="width:100%", _src=URL('download', args = db.image(e.element_data).img )))
        else:
            did.append(P(XML(e.element_data.replace('\n','<br />')), _class="text-element"))
    
    # div for actions
    actions = DIV( _class="did-actions clear")
    
    # follow/unfollow button
    if row.author_id != auth.user_id:
        if str(row.author_id) in following:
            actions.append(A('unfollow', _class="btn form-btn f"+str(row.author_id), _title="unfollow", _onclick="unfollow("+row.author_id+")"))
        else:
            actions.append(A('follow' , _class="btn form-btn f"+str(row.author_id), _title="follow", _onclick="follow("+row.author_id+")"))
        
    # like button
    if db.likes(user_id = auth.user_id, did_id = row.id) != None:
        actions.append(A('unlike', _class="btn form-btn like", _title="Unlike", _onclick="unlike("+str(row.id)+", this)"))
    else:
        actions.append(A('like', _class="btn form-btn dont-like", _title="Like", _onclick="like("+str(row.id)+", this)"))
        
    # number of likes
    actions.append(SPAN( str(row.likes), _class="likes", _id='l'+str(row.id)))
    
    # show/hide/add comment anchors
    comments = db(db.comments.did_id==row.id).select(orderby=~db.comments.date_created)
    actions.append(A('comment', _id="com_btn"+str(row.id), _style="float: right", _class="btn form-btn", _onclick="addComment('d"+str(div_num)+"', "+str(row.id)+", this)"))
    actions.append(A("show comments ("+str(len(comments))+")", _class="toggle-coms", _onclick="toggleComments('com_d"+str(div_num)+"', this)"))
    
    # append actions to did
    did.append(actions)
    
    # comments
    comment_div = DIV( _class="comment-container", _id="com_d"+str(div_num) )
    for c in comments.render():
        comment = DIV( _class="comment")
        com_author = A(B(str(db.users(c.author_id).username) + ' '), _href=URL('default','profile', args=[str(db.users(c.author_id).username)]))
        comment.append(P( com_author, XML(c.body.replace('\n','<br />')), _style="word-break: break-word; margin-bottom: 0px; text-align: left;"))
        comment_div.append(comment)
    did.append(comment_div)
    
    #return DOM element
    return did
    
    
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
              _class='did clear')
    
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
            did.append(IMG( _style="width:100%", _src=URL('download', args = db.image(img_id).img )))
        else:
            db.elements.insert(did_id = did_id,
                stack_num = i,
                is_image = False,
                element_data = str(d))
            did.append(P(XML(linkify(str(d), did_id, author).replace('\n','<br />')), _style="word-break: break-word"))
            
    did.append(P(str(db.users(auth.user_id).username) +' on '+ str(date_created)))

    bottom = DIV( _class="clear")

    bottom.append(HR( _class="did-sep"))
    
    bottom.append(A('like', _class="btn form-btn dont-like", _title="Like", _onclick="like("+str(did_id)+", this)"))
    bottom.append(SPAN( '0', _style="margin-left: 5px;", _class="likes", _id='l'+str(did_id)))
    
    bottom.append(A('comment', _id="com_btn"+str(did_id), _style="float:right", _class="btn form-btn", _onclick="addComment('"+data['div_id']+"', "+str(did_id)+", this)"))
    bottom.append(A("show comments (0)", _class="toggle-coms", _onclick="toggleComments('com_"+data['div_id']+"', this)"));
    bottom.append(DIV( _class="comment-container", _id="com_"+data['div_id'] ))

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
    user = db.users(auth.user_id)
    name = request.args(0)
    editable = False
    if name:
        name = name.lower()
        logging.error('name is         :'+name+'\n')
        if user.username == name: 
            editable = True
        else: 
            find_user = db(db.users.username == name).select().first() 
            logging.error('requested ' + name + "'s profile" )
            logging.error('value of test is:')
            if find_user != None:
                logging.error('found profile' + name + '\n')
                user = find_user
            else:
                redirect(URL('default', 'profile/' + user.username))
    else:
        redirect(URL('default', 'profile/' + user.username))
    about_str = linkify(user.about)
    following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
    dids_left = []
    dids_center = []
    dids_right = []
    if request.args(1) and request.args(1) == 'bucketlist':
        bucket_items = set([row.did_id for row in db(db.bucketlist.user_id == user.user_id).select(db.bucketlist.did_id)])
        dids = db(db.dids.id.belongs(bucket_items)).select(orderby=~db.dids.date_created)
        logging.error('in my bucketlist')
        about_str = linkify(user.about)
        following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
    else:        
        dids = db(db.dids.author_id==user.user_id).select(orderby=~db.dids.date_created)
    if dids:
        i = 0
        for d in dids:
            if i%3 == 0:
                dids_left.append(did2DOM(d, following, i))
            elif i%3 == 1:
                dids_center.append(did2DOM(d, following, i))
            elif i%3 == 2: 
                dids_right.append(did2DOM(d, following, i))
            i += 1
    return dict(dids_left=dids_left, dids_center=dids_center, dids_right=dids_right,
                                    user=user, about_str=about_str, editable=editable)



"""################################################################################################"""
"""###################################################################################################
###########
########### Folowers and Following
###########
###################################################################################################"""

def followers():  
    user = db(db.users.user_id == auth.user.id).select().first()
    name = request.args(0)
    editable = False
    if name:
        name = name.lower()
        if user.username == name: 
            editable = True
        else: 
            test = db(db.users.username == name).select().first() 
            if test != None:
                user = test
            else:
                redirect(URL('default', 'profile/' + user.username))
    else:
        redirect(URL('default', 'followers/' + user.username))
    

    set_followers = set([row.follower_id for row in db(db.followers.following_id == user.user_id).select(db.followers.follower_id)])
    set_following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
    followers = db(db.users.id.belongs(set_followers)).select(orderby=~db.users.first_name)
    for f in followers:
        f.following = str(f.user_id in set_following)
        logging.error("I am following "+f.username+ " = "+ f.following+"\n")
    return dict(user=user, followers=followers)

def following():
    user = db(db.users.user_id == auth.user.id).select().first()
    name = request.args(0)
    editable = False
    if name:
        name = name.lower()
        if user.username == name: 
            editable = True
        else: 
            test = db(db.users.username == name).select().first() 
            if test != None:
                user = test
            else:
                redirect(URL('default', 'profile/' + user.username))
    else:
        redirect(URL('default', 'followers/' + user.username))

    set_following = set([row.following_id for row in db(db.followers.follower_id == user.user_id).select(db.followers.following_id)])
    set_auth_following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
    followers = db(db.users.id.belongs(set_following)).select(orderby=~db.users.first_name)
    for f in followers:
        f.following = str(f.user_id in set_auth_following)
        logging.error("I am following "+f.username+ " = "+ f.following+"\n")
    return dict(user=user, followers=followers)



"""################################################################################################"""
"""###################################################################################################
###########
########### Searching Hashtags and Users
###########
###################################################################################################"""

def find():
    if request.args:
        following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
        hashtags = set([row.did_id for row in db(db.hashtags.hashtag == request.args(0)).select(db.hashtags.did_id)])
        dids = db(db.dids.id.belongs(hashtags)).select(orderby=~db.dids.date_created)
        logging.error(dids)
        hashtag = linkify('#' + request.args(0))
        dids_left = []
        dids_center = []
        dids_right = []
        i=0
        if dids:
            for d in dids:
                if i%3 == 0:
                    dids_left.append(did2DOM(d, following, i))
                elif i%3 == 1:
                    dids_center.append(did2DOM(d, following, i))
                elif i%3 == 2: 
                    dids_right.append(did2DOM(d, following, i))
                i += 1
    else:
        return dict(dids_left=dids_left, dids_center=dids_center, dids_right=dids_right, hashtag='')
    return dict(dids_left=dids_left, dids_center=dids_center, dids_right=dids_right, hashtag=hashtag)



@auth.requires_login()
def add_comment():
    data = request.vars
    
    db.comments.insert(did_id = data['did_id'],
                       date_created = datetime.datetime.utcnow(),
                       author_id = auth.user_id,
                       reply_id = None,
                       body = data['comment'])
    
    comment = DIV( B(str(auth.user.first_name + ' ' + str(auth.user.last_name)))+ ' ' + P(XML(linkify(data['comment'], data['did_id'], auth.user_id).replace('\n','<br />')), _style="word-break: break-word"),
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
 
"""
like a did
""" 
def like():
    data = request.vars
    if not db.likes(did_id = data['did_id'], user_id = auth.user_id):
        db.likes.insert(did_id = data['did_id'],
                            user_id = auth.user_id)
        db(db.dids.id == data['did_id']).update(likes = db.dids(data['did_id']).likes + 1)
        
    return

"""
unlike a did
"""
def unlike():
    data = request.vars
          
    l = db.likes(did_id = data['did_id'], user_id = auth.user_id)
    if l:
        db(db.likes.id==l.id).delete()
        db(db.dids.id == data['did_id']).update(likes = db.dids(data['did_id']).likes - 1)
        
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




