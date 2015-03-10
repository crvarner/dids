
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
REGEX = re.compile('/(^|[^@\w])@(\w{1,15})\b/g')

db.define_table('dids',
                Field('author_id'),
                Field('date_created','datetime'),
                Field('title'),
                Field('likes','integer'),
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


"""################################################################################################
########  Represent users with @ and later represent search criteria with 
########  hashtag marks
################################################################################################"""
"""
def create_redirect_links(s):
    #logging.error('in create_redirect_links: '+ s)
    RE_HASH = re.compile('@([a-zA-Z0-9_])*[:;, ]')
    #match = RE_HASH.match(s)
    def makelink(match):
        # The tile is what the user puts in
        #logging.error('in makelink: '+ match)
        title = match.group(0).strip()
        logging.error(match.group(0).strip())
        logging.error(match.group(1).strip())
        # The page, instead, is a normalized lowercase version.
        page = title.lower()
        page = page[1:]
        return '[[%s %s]]' % (title, '<a href="/dids/default/profile/'+page+'">@'+title+'</a>')
    return re.sub(RE_HASH, makelink, s)

def represent_link_encoded_text(s): 
    #logging.error('in crepresent_link_endoced_text: '+ s)
    return MARKMIN(create_redirect_links(s))

def represent_content(v, r):
    #logging.error('in represent_content: '+ v)
    return represent_link_encoded_text(v)



#db.users.about.represent = represent_content
"""

def create_wiki_links(s):
    """This function replaces occurrences of '<<polar bear>>' in the 
    wikitext s with links to default/page/polar%20bear, so the name of the 
    page will be urlencoded and passed as argument 1."""
    def makelink(match):
        logging.error('in makelink')
        # The tile is what the user puts in
        title = str(match.group(2).strip())
        # The page, instead, is a normalized lowercase version.
        page = title.lower()
        return '[[%s %s]]' % (title, URL('default', 'profile', args=[page]))
    return re.sub(REGEX, makelink, s)

def represent_wiki(s):
    """Representation function for wiki pages.  This takes a string s
    containing markup language, and renders it in HTML, also transforming
    the <<page>> links to links to /default/index/page"""
    return MARKMIN(create_wiki_links(s))

def represent_content(v, r):
    """In case you need it: this is similar to represent_wiki, 
    but can be used in db.table.field.represent = represent_content"""
    return represent_wiki(v)


# We associate the wiki representation with the body of a revision.
db.comments.body.represent = represent_content

"""################################################################################################"""
## store new user in users database on_accpet of registration
def enter_user(myform):
    logging.error(myform.vars.username)
    form = myform.vars
    db.users.insert(user_id=form.id, username=form.username, email=form.email)

auth.settings.register_onaccept = enter_user

