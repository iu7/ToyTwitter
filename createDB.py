# coding: utf-8

from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
#from flask_oauthlib.provider import OAuth2Provider
import json, math
import DB
from logger import Logger

app = Flask(__name__, template_folder='templates')
app.debug = True
app.secret_key = 'BSV88'
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',#'SQLALCHEMY_DATABASE_URI': 'sqlite:///db{timecode}.sqlite'.format(timecode=datetime.utcnow()), # datetime.utcnow()
})
#db = SQLAlchemy(app)

fullDB = DB.getDB(app)
db = fullDB['db']
Users = fullDB['Users']
Session = fullDB['Session']
LoginPas = fullDB['LoginPas']
Subscribes = fullDB['Subscribes']
Notes = fullDB['Notes']
Tags = fullDB['Tags']

SALT_LENGTH = 3
SESSION_EXPIRES = 1000000

log = Logger("db_log.txt", "createDB")

# need to gen procedure

#create
def createUsers():
    u1 = Users(name=None,mail="mail1",registrationTime=datetime.utcnow())
    assert u1 is not None, "Can't create user record this way"
    u2 = Users(name=None,mail="mail2",registrationTime=datetime.utcnow())
    assert u2 is not None, "Can't create user record this way"
    
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    log.write("Users create new records")

def createSession():
    u = Users.query.filter_by(id=1).first()
    if u:
        s = Session(userId=u.id, accessToken=gen_salt(SALT_LENGTH), expires=datetime.utcnow() + timedelta(seconds=SESSION_EXPIRES))
        db.session.add(s)
        db.session.commit()
        log.write("Session create new record")
    else:
        log.write("Session can't create new record", 1)

def createLoginPas():
    u = Users.query.filter_by(id=1).first()
    if u:
        lp = LoginPas(userId=u.id, login="user1", password="1")
        db.session.add(lp)
        db.session.commit()
        log.write("LoginPas create new record")
    else:
        log.write("LoginPas can't create new record", 1)

def createNotes():
    u = Users.query.filter_by(id=1).first()
    if u:
        n = Notes(userId=u.id, note="Hello world", repost=False, registrationTime=datetime.utcnow())
        db.session.add(n)
        db.session.commit()
        log.write("LoginPas create new record")
    else:
        log.write("Notes can't create new record", 1)

def createRepost():
    u = Users.query.filter_by(id=2).first()
    n = Notes.query.filter_by(id=1).first()
    if u and n:
        r = Notes(userId=u.id, repost=True, repostId=n.id, registrationTime=datetime.utcnow())
        Notes.query.filter_by(id=1).update({'repostCount': n.repostCount + 1})
        db.session.add(r)
        db.session.commit()
        log.write("LoginPas create new repost-record")
    else:
        log.write("Notes can't create new repost-record", 1)

def createSub():
    u1 = Users.query.filter_by(id=1).first()
    u2 = Users.query.filter_by(id=2).first()
    if u1 and u2:
        s = Subscribes(userId=u1.id, subId=u2.id)
        db.session.add(s)
        db.session.commit()
        log.write("Subscribes create new record")
    else:
        log.write("Subscribes can't create new record", 1)

def createTag():
    n = Notes.query.filter_by(id=1).first()
    if n:
        t = Tags(tagName="hello", noteId=n.id)
        db.session.add(t)
        db.session.commit()
        log.write("Tag create new record")
    else:
        log.write("Tag can't create new record", 1)


# delete
def deleteNote():
    n = Notes.query.filter_by(id=1).first()
    if n:
        db.session.delete(n)
        db.session.commit()
        log.write("Note is deleted")
        n = Notes.query.filter_by(repostId=1).first()
        if not n:
            log.write("subNote are deleted")
        else:
            log.write("subNote aren't deleted", 1)
        t = Tags.query.filter_by(noteId=1).first()
        if not t:
            log.write("Tags are deleted")
        else:
            log.write("Tags aren't deleted", 1)
        
def deleteUser():
    u = Users.query.filter_by(id=1).first()
    if u:
        db.session.delete(u)
        db.session.commit()
        log.write("User is deleted")
        n = Notes.query.filter_by(userId=1).first()
        if not n:
            log.write("Note is deleted")
            n = Notes.query.filter_by(repostId=1).first()
            if not n:
                log.write("subNote is deleted")
            else:
                log.write("subNote isn't deleted", 1)
            t = Tags.query.filter_by(noteId=1).first()
            if not t:
                log.write("Tags are deleted")
            else:
                log.write("Tags aren't deleted", 1)
        else:
            log.write("Note isn't deleted", 1)
        lp = LoginPas.query.filter_by(userId=1).first()
        if not lp:
            log.write("LoginPas is deleted")
        else:
            log.write("LoginPas isn't deleted", 1)



def createTest():
    createUsers()
    createSession()
    createLoginPas()
    createNotes()
    createRepost()
    createSub()
    createTag()
    
def deleteTest():
    #deleteNote() # done
    deleteUser()



if __name__ == '__main__':
    db.create_all()
    # create test
    #createTest()
    # read test
    # pass
    # update test
    # pass
    # delete test
    #deleteTest()
    #app.run(debug=True)

