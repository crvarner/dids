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
import base64
import re


@auth.requires_login()
def index():
    #response.flash = 'auth.username = '+str(auth.user.username)

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
        """elif request.args and request.args[0] == 'followers':
        authors = [row.follower_id for row in db(db.followers.following_id == auth.user_id).select(db.followers.follower_id)]
        dids = db(db.dids.author_id.belongs(authors)).select(orderby=~db.dids.date_created)  """     
    else:
        authors = following | set(str(auth.user_id))
        dids = db(db.dids.author_id.belongs(authors)).select(orderby=~db.dids.date_created)

    i = 0;
    ds = []
    for d in dids:
        ds.append(did2DOM(row = d, following = following, div_num = i))
        i += 1
        
    return dict(dids=ds)

    
def did2DOM(row, div_num, following=set(), new=False):
    """ things I need to pass
    did db row
    following
    div_num
    """
    
    #create did
    if not new:
        did = DIV( _class="did clear", _id="d"+ str(div_num) )
    elif new:
        did = DIV( _class="did clear", _id=str(div_num) )
    
    #attach author
    did.append(A(db.users(row.author_id).username, _href=URL('default','profile', args=[db.users(row.author_id).username]), _class="did-author"))
    
    # attach title
    if row.title != '':
        did.append(H4(XML(linkify(row.title)), _class="did-title"))
    
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
    if str(row.author_id) != str(auth.user_id) and not new:
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
    
    # allows for linkify in title after first post
    linkify(s = str(data['did_title']), did_id = did_id, user_id = author)

    
    num_elems = (len(data) - 2)/2
    for i in range(0, num_elems):
        d = data['elem'+str(i)]
        if (data['is_img' + str(i)] == 'True'):
            # trim away JSON attributes
            image = re.search(r'base64,(.*)', str(d)).group(1)
            # open file and write decoded binary
            output = open('anon.jpeg', 'wb+')
            # write file in temp file object
            output.write(str(base64.b64decode(image)))
            # move file pointer to beginning for rewriting in DB
            output.seek(0,0) 
            # for error checking print index of filewriter cursor element
            #logging.error(output.tell())
            # store image file in db
            #logging.error(d)
            # throw image into image db
            img_id = db.image.insert(img = db.image.img.store(output, 'anon.jpeg'))
            # throw element number into did id
            db.elements.insert(did_id = did_id,
                stack_num = i,
                is_image = True,
                element_data = img_id)
            #did.append(IMG( _style="width:100%", _src=URL('download', args = db.image(img_id).img )))
        else:
            db.elements.insert(did_id = did_id,
                stack_num = i,
                is_image = False,
                element_data = str(d))
            # redundant but necessary 
            linkify(s = str(d), did_id = did_id, user_id = author)
    
    return did2DOM( row = db.dids(did_id) , div_num = data['div_id'], new = True )
    

"""###################################################################################################
###########
########### profile
###########
###################################################################################################"""

@auth.requires_login()
def update_profile():
    data = request.vars
    user = db.users(auth.user_id)
    user_id = auth.user.id
    
    # if an updated about in vars update user's about 
    about_str = ''
    if(data['about']):
        #logging.error('updating about\n')
        logging.error(linkify(data['about']))
        db(db.users.user_id == user_id).update(about=str(data['about']))
        #logging.error('updated about\n')
    elif(data.is_profile):
        
    
       
        # find start of base64 string from urldata
        image = re.search(r'base64,(.*)', str(data.file)).group(1)

        # open file and write decoded binary
        output = open(str('TEMP.JPEG'), 'wb+')
        output.write(str(base64.b64decode(image)))
        # move file pointer to beginning for rewriting in DB
        output.seek(0,0) 
        logging.error(output.tell())

        #delete old profile img
        if user.profile_img: db(db.profile_image.id==user.profile_img).delete()
        # store image file in db
        new_img = db.profile_image.insert(img = db.profile_image.img.store(output, data.filename))
        logging.error('the new id of the image is ' + str(new_img))
        db(db.users.user_id == user_id).update(profile_img=new_img)
        output.close()

        
    elif(data.is_background):

        
        # find start of base64 string from urldata
        image = re.search(r'base64,(.*)', str(data.background)).group(1)

        # open file and write decoded binary
        output = open(str('TEMP.JPEG'), 'wb+')
        output.write(str(base64.b64decode(image)))
        # move file pointer to beginning for rewriting in DB
        output.seek(0,0) 
        logging.error(output.tell())

        #delete old profile img
        if user.profile_background_img: db(db.profile_image.id==user.profile_background_img).delete()
        # store image file in db
        new_img = db.profile_image.insert(img = db.profile_image.img.store(output, data.filename))
        
        db(db.users.user_id == user_id).update(profile_background_img=new_img)
        output.close()

    return 


@auth.requires_login()
def profile():
    #session.flash = 'auth.user_id = ' + str(auth.user_id)

    user = db.users(auth.user_id)
    name = request.args(0)

    editable = False
    if name:
        name = name.lower()
        #logging.error('name is         :'+name+'\n')
        if name == 'bucketlist':
            redirect(URL('default', 'profile', args =  [user.username, 'bucketlist']))
        if user.username == name: 
            editable = True
        else: 
            find_user = db(db.users.username == name).select().first() 
            #logging.error('requested ' + name + "'s profile" )
            #logging.error('value of test is:')
            if find_user != None:
                #logging.error('found profile' + name + '\n')
                user = find_user
            else:
                redirect(URL('default', 'profile', args =[user.username]))
    else:
        redirect(URL('default', 'profile', args = [user.username]))
    about_str = linkify(user.about)
    user_img = URL('download', URL('static', args=['images', 'face.png']))
    if user.profile_img: user_img = URL('download', args = db.profile_image(user.profile_img).img)
    else: user_img = None
    if user.profile_background_img: user_background_img = URL('download', args = db.profile_image(user.profile_background_img).img)
    else: user_background_img = None
    following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
    dids_left = []
    dids_center = []
    dids_right = []
    form = form = SQLFORM.factory(Field('body', 'text',
                                     label='About',
                                     default=user.about
                                     ))

    if request.args(1) and request.args(1) == 'bucketlist':
        bucket_items = set([row.did_id for row in db(db.bucketlist.user_id == user.user_id).select(db.bucketlist.did_id)])
        dids = db(db.dids.id.belongs(bucket_items)).select(orderby=~db.dids.date_created)
        #logging.error('in my bucketlist')
        about_str = linkify(user.about)
        following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
    else:        
        dids = db(db.dids.author_id==user.user_id).select(orderby=~db.dids.date_created)
    if dids:
        i = 0
        for d in dids:
            if i%3 == 0:
                dids_left.append(did2DOM(row = d, following = following, div_num = i))
            elif i%3 == 1:
                dids_center.append(did2DOM(row = d, following = following, div_num = i))
            elif i%3 == 2: 
                dids_right.append(did2DOM(row = d, following = following, div_num = i))
            i += 1
    return dict(dids_left=dids_left, dids_center=dids_center, dids_right=dids_right,
                                    user=user, user_img=user_img, user_background_img=user_background_img,
                                    about_str=about_str, editable=editable, form=form)



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
    follow_DOM = DIV (_id="center-main-conatiner", _class="did-span")
    for f in followers:
        f.following = str(f.user_id in set_following)
        if (f.following == True):
            follow_DOM.append(DIV( IMG( _class="followers_image_preview", 
                _src=URL('download', args=[db.profile_image(f.profile_img).img])), 
                A( "unfollow", _class="btn form-btn followers_listing_follow_btn" 
                ,_id="f"+str(f.user_id), _title="unfollow", _onclick="local_unfollow("+f.user_id+")"), 
                A(f.username, _href=URL('profile', args=[f.username]), _id="followers_listing_username"),
                 _class="followers_listing"))
        else: follow_DOM.append(DIV( IMG( _class="followers_image_preview", 
                _src=URL('download', args=[db.profile_image(f.profile_img).img])), 
                A( "unfollow", _class="btn form-btn followers_listing_follow_btn" 
                ,_id="f"+str(f.user_id), _title="follow", _onclick="local_unfollow("+f.user_id+")"), 
                A(f.username, _href=URL('profile', args=[f.username]), _id="followers_listing_username"), 
                _class="followers_listing"))
    return dict(follow_DOM = follow_DOM)


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
        redirect(URL('default', 'following/' + user.username))

    set_following = set([row.following_id for row in db(db.followers.follower_id == user.user_id).select(db.followers.following_id)])
    set_auth_following = set([row.following_id for row in db(db.followers.follower_id == auth.user_id).select(db.followers.following_id)])
    followers = db(db.users.id.belongs(set_following)).select(orderby=~db.users.first_name)
    follow_DOM = DIV (_id="center-main-container", _class="did-span")
    for f in followers:
        f.following = str(f.user_id in set_auth_following)
        if (f.following == True):
            follow_DOM.append(DIV( IMG( _class="followers_image_preview", 
                _src=URL('download', args=[db.profile_image(f.profile_img).img])), 
                A( "unfollow", _class="btn form-btn followers_listing_follow_btn" 
                ,_id="f"+str(f.user_id), _title="unfollow", _onclick="local_unfollow("+f.user_id+")"), 
                A(f.username, _href=URL('profile', args=[f.username]), _id="followers_listing_username"),
                 _class="followers_listing"))
        else: follow_DOM.append(DIV( IMG( _class="followers_image_preview", 
                _src=URL('download', args=[db.profile_image(f.profile_img).img])), 
                A( "unfollow", _class="btn form-btn followers_listing_follow_btn" 
                ,_id="f"+str(f.user_id), _title="follow", _onclick="local_unfollow("+f.user_id+")"), 
                A(f.username, _href=URL('profile', args=[f.username]), _id="followers_listing_username"), 
                _class="followers_listing"))
    return dict(follow_DOM = follow_DOM)



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
        hashtag = linkify('#' + request.args(0))
        dids_left = []
        dids_center = []
        dids_right = []
        i=0
        if dids:
            for d in dids:
                if i%3 == 0:
                    dids_left.append(did2DOM(row = d, following = following, div_num = i))
                elif i%3 == 1:
                    dids_center.append(did2DOM(row = d, following = following, div_num = i))
                elif i%3 == 2: 
                    dids_right.append(did2DOM(row = d, following = following, div_num = i))
                i += 1
    else:
        return dict(dids_left=dids_left, dids_center=dids_center, dids_right=dids_right, hashtag='')
    return dict(dids_left=dids_left, dids_center=dids_center, dids_right=dids_right, hashtag=hashtag)


"""###################################################################################################
##########
########## Notifications
##########
####################################################################################################"""

def notifications():  
    user = db(db.users.user_id == auth.user.id).select().first()
    name = request.args(0)
    if (name != user.username): redirect(URL('notifications', args=user.username))
    set_nots = db(db.notifications.receiver == user.user_id).select(orderby=~db.notifications.time_stamp)
    notifications_DOM =  DIV (_id="center-main-container", _class="did-span")
    
    if set_nots:
        for n in set_nots:
            did = ""
            if (n.did_id): 
                elems = db(db.elements.did_id==n.did_id).select(orderby=db.elements.stack_num)
                for e in elems:
                    if e.is_image:
                        did = (IMG( _src=URL('download', args = db.image(e.element_data).img ), _class="not_img_preview"))
                        break
            logging.error(did)
            sender = db(db.users.user_id == n.sender).select().first()
            if (n.not_action == "liked"):
                notifications_DOM.append(DIV( IMG( _class="followers_image_preview", 
                    _src=URL('download', args=[db.profile_image(sender.profile_img).img])), did,
                    DIV(A(sender.username, _href=URL('profile', args=[sender.username])), " liked your did.",  _id="not_listing_text"),
                    _class="followers_listing"))
            elif (n.not_action == "followed"):
                notifications_DOM.append(DIV( IMG( _class="followers_image_preview", 
                    _src=URL('download', args=[db.profile_image(sender.profile_img).img])),  
                    DIV(A(sender.username, _href=URL('profile', args=[sender.username])), " started following you.",  _id="not_listing_text"),
                     _class="followers_listing"))
            elif (n.not_action == "commented"):
                notifications_DOM.append(DIV( IMG( _class="followers_image_preview", 
                    _src=URL('download', args=[db.profile_image(sender.profile_img).img])),  did,
                    DIV(A(sender.username, _href=URL('profile', args=[sender.username])), " commented on your did.",  _id="not_listing_text"),
                     _class="followers_listing"))
           

    return dict(notifications_DOM=notifications_DOM)





@auth.requires_login()
def add_comment():
    data = request.vars
    
    db.comments.insert(did_id = data['did_id'],
                       date_created = datetime.datetime.utcnow(),
                       author_id = auth.user_id,
                       reply_id = None,
                       body = data['comment'])
    
    linked_string = linkify(str(data['comment']), data['did_id'], auth.user_id).replace('\n','<br />')
    
    comment = DIV( _class="comment")
    com_author = A(B(str(db.users(auth.user_id).username) + ' '), _href=URL('default','profile', args=[str(db.users(auth.user_id).username)]))
    comment.append(P( com_author, XML(linked_string), _style="word-break: break-word; margin-bottom: 0px; text-align: left;"))
    receiver_id = db(db.dids.id == data['did_id']).select().first().author_id
    db.notifications.insert(sender = auth.user_id, receiver = receiver_id,
                            not_action = "commented", did_id = data['did_id']) 
    return comment
    

"""
follow() called via AJAX adds an entry to the followers table
"""

def follow():
    data = request.vars
    
    if not db.followers(following_id = data['following_id'], follower_id = auth.user_id):
        db.followers.insert(following_id = data['following_id'],
                            follower_id = auth.user_id)
        db.notifications.insert(sender = auth.user_id, receiver = data['following_id'],
                            not_action = "followed")
    return
    
"""
unfollow() called via AJAX deletes entry from the followers table
"""


def unfollow():
    data = request.vars

    f = db.followers(following_id = data['following_id'], follower_id = auth.user_id)
    if f:
        db(db.followers.id==f.id).delete()
        #db.notifications.insert(sender = auth.user_id, receiver = data['following_id'],
        #                    not_action = "unfollowed")
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
        receiver_id = db(db.dids.id == data['did_id']).select().first().author_id
        db.notifications.insert(sender = auth.user_id, receiver = receiver_id,
                            not_action = "liked", did_id = data['did_id'])
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
        receiver_id = db(db.dids.id == data['did_id']).select().first().author_id
        db.notifications.insert(sender = auth.user_id, receiver = receiver_id,
                            not_action = "unliked", did_id = data['did_id'])
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




