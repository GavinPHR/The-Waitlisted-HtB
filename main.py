from flaskblog import app
from flaskblog import db
from threading import *
from flaskblog.models import *

def match(data):
    #[{user:[languages]}]
    matches = [{} for i in range(len(data))]
    for i in range(len(data)):
        #Username of user i
        u_i = data[i].get("id")
        #Unknown Languages for user i
        ul_i = data[i].get("language_learn")
        #Known Languages for user i
        kl_i = data[i].get("language_know")
        for j in range(len(data)):
            if i == j:
                continue
            # Username of user j
            u_j = data[j].get("id")
            # Unknown Languages for user j
            ul_j = data[j].get("language_learn")
            # Known Languages for user j
            kl_j = data[j].get("language_know")
            if len(set(ul_i) & set(kl_j)) != 0 and len(set(kl_i) & set(ul_j)) != 0:
                matches[i][u_j] = list(set(ul_i) & set(kl_j))

    for n in range(len(data)):
        user_id = data[n]["id"]
        user=User.query.get(user_id)
        user.match="2"
        db.session.commit()

        for key, values in matches[n].items():
            match_user = key
            for value in values:
                match = Matches(user1_id=user_id,user2_id=match_user, language=value)
                db.session.add(match)
                db.session.commit() 
                        


class trigger_matching(Thread):
    def run(self):
        while(True):
            count = 0
            for n in User.query.filter_by(match="1"):
                count += 1
            if count >= 4:
                print("a")
                data = [ {
                        'id': user.id,
                        'language_know': [ll.language for ll in user.language_know],
                        'language_learn': [ll.language for ll in user.language_learn]
                    } for user in User.query.filter_by(match='1').all()]

                match(data)
   
 
t2 = trigger_matching()
t2.start()

app.run(debug=True)
