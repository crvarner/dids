
import datetime
import unittest
import json
import os
import re
"""
defines the table "dids" which is responsible for
holding reference info for all dids in the system.
The following information is stored:

author_id
date_created
title (optional)
likes (count of likes)
spam (count of 'marked as spam/invalid')
link (optional link to external site)
"""

# Format for wiki links.
RE_LINKS = re.compile('(<<)(.*?)(>>)')
# Format for @usernames
RE_USERS = re.compile('(?<=^|(?<=[^a-zA-Z0-9-_\\.]))@([A-Za-z]+[A-Za-z0-9_]+)')
# Format for #hashtags
RE_HASH = re.compile('\B#([^,\W]+)')

db.define_table('dids',
                Field('author_id'),
                Field('date_created','datetime'),
                Field('title'),
                Field('likes','integer', default=0),
                Field('spam','integer'),
                Field('link')
                )
                
"""
defines the table holding all the contents of all the dids
in the system. this includes gifs, image id's, text bodies, and
videos (potentially)
"""

db.define_table('elements',
                Field('did_id'),
                Field('stack_num','integer'),
                Field('is_image','boolean'),
                Field('element_data')
                )


"""
Define the table holding hashtag data
"""

db.define_table('hashtags',
                Field('did_id'),
                Field('hashtag', 'text'),
                Field('date_hashed'),
                )
db.hashtags.date_hashed.default = datetime.datetime.utcnow()



"""
Define the table holding bucketlist data
"""

db.define_table('bucketlist',
                Field('did_id'),
                Field('user_id'),
                Field('date_bucketed'),
                )
db.bucketlist.date_bucketed.default = datetime.datetime.utcnow()






"""
defines table that will hold image locations on FS
"""
db.define_table('image',
                Field('img','upload'))


"""
defines table that will hold image locations on FS
"""
db.define_table('profile_image',
                Field('img','upload'))

"""
defines the table holding all comments for all dids.
"""

db.define_table('comments',
                Field('did_id'),
                Field('date_created', 'datetime'),
                Field('author_id'),
                Field('reply_id'),
                Field('body','text')
                )
     
                
"""
defines the table holding all "likes"
"""
                
db.define_table('likes',
                Field('user_id'),
                Field('did_id')
                )


"""#########################################################################################
#######
#######   users table 
#######
##########################################################################################"""
def get_user_name():
    s = ''
    if auth.user_id:
        s = auth.user.first_name
    else:
        s = 'John Doe'
    return s

    
"""
defines the table holding all "likes"
"""
                
db.define_table('followers',
                Field('follower_id'),
                Field('following_id')
                )
    
"""
defines table holding user information
"""
db.define_table('users',
                Field('user_id',),
                Field('username'),
                Field('first_name'),
                Field('last_name'),
                Field('profile_img'),
                Field('profile_background_img'),
                Field('about', 'text'),
                Field('email'),
                Field('dids', 'reference dids'),
                Field('feed'),
                Field('numDids'),
                Field('numFollowers'),
                Field('numFollowing'),
                Field('numBucket'),
                Field('numDidBucket'),
                )
#db.users.profile_img.default=os.path.join(request.folder, 'static', 'images', 'facebook.png')
db.users.username.default = IS_NOT_IN_DB(db, db.users)
db.users.username.default = get_user_name()
db.users.username.requires = IS_LOWER()
db.users.user_id.requires = IS_NOT_IN_DB(db, db.users)
db.users.user_id.requires = IS_IN_DB(db, db.auth_user.id)
db.users.user_id.default = auth.user_id
db.users.about.default = ''


"""##################################################################################################
########  Represent users with @ and later represent search criteria with 
########  hashtag marks
"""##################################################################################################"""
def regex_users(s):
    def makelink(match):
        title = match.group(0).strip()
        page = match.group(1).lower()
        return '%s' % (A(title, _href=URL('default', 'profile', args=[page])))

    return re.sub(RE_USERS, makelink, s) 

def regex_hash(s, did_id, user_id):
    def makelink(match):
        title = match.group(0).strip()
        page = match.group(1).lower()
        if did_id != None: 
            logging.error(str(id) + page +'\n')
            db.hashtags.insert(hashtag=page, did_id=did_id)
            if page == 'bucketlist': db.bucketlist.insert(did_id=did_id, user_id=user_id)
        return '%s' % (A(title, _href=URL('default', 'find', args=[page])))

    return re.sub(RE_HASH, makelink, s)

def linkify(s, did_id=None, user_id=None):
    return regex_hash(regex_users(s), did_id, user_id)

def represent_links(s, v):
    return linkify(s)

"""################################################################################################"""
## store new user in users database on_accpet of registration
##
"""################################################################################################"""
def enter_user(myform):
    logging.error(myform.vars.username)
    form = myform.vars
    db.users.insert(user_id=form.id, 
                    username=form.username, 
                    email=form.email, 
                    first_name=form.first_name,
                    last_name=form.last_name,
                    )

"""################################################################################################"""
###  Validation and Representation statements
###
"""################################################################################################"""
auth.settings.register_onaccept = enter_user 
db.dids.title.represent = represent_links 
db.comments.body.represent = represent_links 
db.elements.element_data.represent = represent_links