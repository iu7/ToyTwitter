# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from flask import Flask, url_for
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider
import json, math
from logger import Logger
import DB
from config import Config
import sys
import re

reload(sys)  
sys.setdefaultencoding('utf8')

app = Flask(__name__, template_folder='templates')
app.debug = True
app.secret_key = 'secret'
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})
fullDB = DB.getDB(app)
db = fullDB['db']
Users = fullDB['Users']
Subscribes = fullDB['Subscribes']
Notes = fullDB['Notes']
Tags = fullDB['Tags']

log = Logger("feed_log.txt", "Feed")
config = Config()

# make global
# select tags

def pagination(p, pp, count):
    if pp <= 0:
        pp = count
        max_page = 1
    else:
        max_page = int(math.ceil(count * 1.0 / pp)) 
    return p, pp, max_page

def getJSONdata(url, method, methodName=""):
    log.write("{methodType} {method} was called".format(methodType=method, method=methodName))
    if method == 'GET':
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req)
        answ = json.loads(resp.read())
    else:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url)
        req.get_method = lambda: method
        resp = opener.open(req)
        answ = json.loads(resp.read())
    if not ('error' in answ):
        log.write("Success {methodType} {method} call".format(methodType=method, method=methodName))
        return answ, False
    log.write("Fail with {methodType} {method} call".format(methodType=method, method=methodName), 1)
    return answ, True

# get_feed

@app.route('/api/rest_feed',  methods=['GET', 'POST', 'DELETE'])
def rest_feed():
    log.write("{method} rest_feed has been called".format(method=request.method))
    if request.method == 'GET':
        userId = request.args.get('userId', '')
        following = Subscribes.query.filter_by(userId=userId).all()
        usersId = []
        for f in following:
            usersId.append(f.subId)
        usersId.append(userId)

        p = int(request.args.get('p', config.DEFAULT_PAGE))
        pp = int(request.args.get('pp', config.DEFAULT_PER_PAGE))
        parentNotes = db.aliased(Notes, name='parent_notes')
        #notes = db.session.query(Notes.id, Notes.userId, Notes.repost, Notes.repostId, Notes.note, Notes.repostCount).outerjoin(parentNotes, Notes.id == parentNotes.repostId).filter(Notes.userId.in_(usersId), or_(Notes.userId != userId, parentNotes.repostId == None))
        #notes = db.session.query(Notes.id, Notes.userId, Notes.repost, Notes.repostId, Notes.note, Notes.repostCount).outerjoin(parentNotes, Notes.id == parentNotes.repostId).filter(Notes.userId.in_(usersId))
        notes = db.session.query(Notes.id, Notes.userId, Notes.repost, Notes.repostId, Notes.note, Notes.repostCount, Notes.registrationTime).order_by(Notes.id.desc()).filter(Notes.userId.in_(usersId))
        iid = 0
        iuserId = 1
        irepost = 2
        irepostId = 3
        inote = 4
        irepostCount = 5
        iregistrationTime = 6

        count = notes.count()
        p, pp, max_page = pagination(p, pp, count)
        notes = notes.offset((p-1)*pp).limit(pp).all()
        log.write(notes)
        array = []
        # forgive me father for i have sinned
        for n in notes:
            u = Users.query.filter_by(id=n[iuserId]).first()
            if n[irepost]:
                r = Notes.query.filter_by(id=n[irepostId]).first()
                ur = Users.query.filter_by(id=r.userId).first()
                array.append({'id': n[iid], 'userId': n[iuserId], 'name': u.name, 'note': r.note, 'isRepost': n[irepost], 'repostId': n[irepostId], 
                              'repostUserId': r.userId, 'repostName': ur.name, 'repostCount': r.repostCount,  'registrationTime': n[iregistrationTime].strftime("%d/%m/%y %H:%M")})
            else:
                array.append({'id': n[iid], 'userId': n[iuserId], 'name': u.name, 'note': n[inote], 'isRepost': n[irepost], 'repostCount': n[irepostCount], 'registrationTime': n[iregistrationTime].strftime("%d/%m/%y %H:%M")})
        return json.dumps({'elements': array, 'page': p, 'max_page': max_page, 'count': count})
    if request.method == 'POST':
        # repost check
        userId = request.args.get('userId', '')
        isRepost = request.args.get('isRepost', 'False')
        repostId = request.args.get('repostId', '')
        note = request.form.get('note', '')
        registrationTime = datetime.utcnow()
        user = Users.query.filter_by(id=userId).first()
        if user:
            if isRepost == 'True' or isRepost == '1':
                r = Notes.query.filter_by(id=repostId).first()
                if not r.repost:
                    n = Notes(userId=userId, repost=True, repostId=repostId, repostCount=0, registrationTime=registrationTime, note=None)
                    db.session.add(n)
                    db.session.commit()
            else:
                n = Notes(userId=userId, repost=False, repostId=None, repostCount=0, registrationTime=registrationTime, note=note)
                db.session.add(n)
                db.session.commit()
                tags = set(x for x in re.findall('(#[^ ]*)', note))
                log.write(tags)
                for t in tags:
                    tag = Tags(noteId=n.id, tagName=t[1:])
                    db.session.add(tag)
                db.session.commit()
            return jsonify(answer='Success')
    if request.method == 'DELETE':
        userId = request.args.get('userId', '')
        noteId = request.args.get('noteId', '')
        n = Notes.query.filter_by(id=noteId).first()
        if n:
            log.write(userId)
            log.write(n.userId)
            log.write(n.repost)
            if int(n.userId) == int(userId):
                db.session.delete(n)
                db.session.commit()
                return jsonify(answer='Success')
    log.write("{method} rest_feed return an error".format(method=request.method), 1)
    return jsonify(error='1')

@app.route('/api/user_feed',  methods=['GET'])
def user_feed():
    log.write("user_feed has been called")
    userId = request.args.get('userId', '')
    if not userId:
        log.write("user_feed return an error", 1)
        return jsonify(error='1')

    p = int(request.args.get('p', config.DEFAULT_PAGE))
    pp = int(request.args.get('pp', config.DEFAULT_PER_PAGE))
    count = Notes.query.filter_by(userId=userId).count()
    
    p, pp, max_page = pagination(p, pp, count)
    notes = Notes.query.order_by(Notes.id.desc()).filter_by(userId=userId).join(Users, Notes.userId==Users.id).add_columns(
        Users.name, Notes.id, Notes.userId, Notes.note, Notes.repost, Notes.repostId, Notes.repostCount, Notes.registrationTime).offset((p-1)*pp).limit(pp).all()
    
    array = []
    # forgive me father for i have sinned
    for n in notes:
        if n.repost:
            r = Notes.query.filter_by(id=n.repostId).first()
            u = Users.query.filter_by(id=r.userId).first()
            array.append({'id': n.id, 'userId': n.userId, 'name': n.name, 'note': r.note, 'isRepost': n.repost, 'repostId': n.repostId, 
                          'repostUserId': r.userId, 'repostName': u.name, 'repostCount': r.repostCount, 'registrationTime': n.registrationTime.strftime("%d/%m/%y %H:%M")})
        else:
            array.append({'id': n.id, 'userId': n.userId, 'name': n.name, 'note': n.note, 'isRepost': n.repost, 'repostCount': n.repostCount, 'registrationTime': n.registrationTime.strftime("%d/%m/%y %H:%M")})

    return json.dumps({'elements': array, 'page': p, 'max_page': max_page, 'count': count})


if __name__ == '__main__':
    assert len(sys.argv) == 6, "Front needs services ports"
    config.load_config(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    app.run(host='localhost', port=config.FEED_PORT, debug=True)
