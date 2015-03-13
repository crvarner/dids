
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
RE_USERS = re.compile('(?<=^|(?<=[^a-zA-Z0-9-_\\.]))@([A-Za-z]+[A-Za-z0-9_]+)')

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
defines table that will hold image locations on FS
"""
db.define_table('image',
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
                Field('profile_img', 'upload'),
                Field('about', 'text'),
                Field('email'),
                Field('dids', 'reference dids'),
                Field('users_followers', 'reference users'),
                Field('users_following', 'reference users'),
                Field('feed'),
                )
db.users.profile_img.default = os.path.join(request.folder, 'static', 'images', 'facebook.png')
db.users.username.default = IS_NOT_IN_DB(db, db.users)
db.users.username.default = get_user_name()
db.users.user_id.requires = IS_NOT_IN_DB(db, db.users)
db.users.user_id.requires = IS_IN_DB(db, db.auth_user.id)
db.users.user_id.default = auth.user_id
db.users.about.default = ''


"""##################################################################################################
########  Represent users with @ and later represent search criteria with 
########  hashtag marks
"""##################################################################################################"""
def regex_text(s):
    logging.error('in regex_text\n')
    logging.error(s)
    result = RE_USERS.search(s)
    def makelink(match):
        logging.error('in makelink')
        # The tile is what the user puts in
        title = match.group(0).strip()
        # The page, instead, is a normalized lowercase version.
        page = title.lower()
        return '%s' % (A(title, _href=URL('default', 'profile', args=[page])))
    logging.error('exit regex text\n')
    return re.sub(RE_USERS,makelink, s) 

def linkify(s):
    return regex_text(s)

def represent_links(s, v):
    return linkify(s)

"""################################################################################################"""
## store new user in users database on_accpet of registration
##
"""################################################################################################"""
def enter_user(myform):
    logging.error(myform.vars.username)
    form = myform.vars
    db.users.insert(user_id=form.id, username=form.username, email=form.email)

auth.settings.register_onaccept = enter_user
db.comments.body.represent = represent_links 
