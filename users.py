
from flaskblog.models import User

import _thread
import time

def matchUsers():
    return [ {
        'id': user.id,
        'language_know': [ll.language for ll in user.language_know],
        'language_learn': [ll.language for ll in user.language_learn]
    } for user in User.query.filter_by(match='1').all()]


def triggerMatchingThread():
    pass

def triggerMatching():
    try:
        _thread.start_new_thread(triggerMatchingThread)
    except:
        print("Error: unable to start thread")
