
from flaskblog.models import User, Know, Learn

User = {
    'language_know'
    'language_learn'
    #'language_practice'
}

def getUsers():
    print(Know.query.all())
    print(Learn.query.all())
    users = {}

    for k in Know.query.all():
        if not users.has_key(k):
            users[k] = [];

        #users[k] =
