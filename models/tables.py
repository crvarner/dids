
import datetime
import json

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
