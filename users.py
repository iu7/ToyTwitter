# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider
import json, math
from logger import Logger
import DB
from config import Config
import sys

reload(sys)  
sys.setdefaultencoding('utf8')

log = Logger("users_log.txt", "Users")
config = Config()

app = Flask(__name__, template_folder='templates')
app.debug = True
app.secret_key = 'secret'
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})
fullDB = DB.getDB(app)
db = fullDB['db']
Users = fullDB['Users']
LoginPas = fullDB['LoginPas']
Subscribes = fullDB['Subscribes']

# make global

def pagination(p, pp, count):
    if pp <= 0:
        pp = count
        max_page = 1
    else:
        max_page = int(math.ceil(count * 1.0 / pp))
        
    if (p < 1) or (p > max_page):
        p = max_page

    return p, pp, max_page


@app.route('/api/user_by_login', methods=['GET'])
def api_user_by_login():
    log.write("user_by_session has been called")
    login = request.args.get('login', '')
    pas = request.args.get('pas', '')
    user = LoginPas.query.filter_by(login=login, password=pas).first()
    if user:
        return jsonify(userId=user.userId)
    log.write("user_by_login return an error", 1)
    return jsonify(error='2', error_message='Неправильный логин или пароль')

#get full
@app.route('/api/user_access',  methods=['GET'])
def api_user_acess():
    log.write("user_acess has been called")
    userId = request.args.get('userId', '')
    user = Users.query.filter_by(id=userId).first()
    if user:
        return jsonify(id=user.id, name=user.name, registrationTime=user.registrationTime, mail=user.mail)
    log.write("user_acess return an error", 1)
    return jsonify(error='1')

@app.route('/api/followers',  methods=['GET'])
def api_followers():
    log.write("followers has been called")
    userId = request.args.get('userId', '')
    if not userId:
        log.write("followers return an error", 1)
        return jsonify(error='1')

    p = int(request.args.get('p', config.DEFAULT_PAGE))
    pp = int(request.args.get('pp', config.DEFAULT_PER_PAGE))
    count = Subscribes.query.filter_by(subId=userId).count()
    
    p, pp, max_page = pagination(p, pp, count)
    followers = Subscribes.query.filter_by(subId=userId).offset((p-1)*pp).limit(pp).all()
    users = db.session.query(Users.id, Users.name).filter(Users.id.in_(tuple(f.userId for f in followers))).all()
    array = []
    for u in users:
        array.append({'userId': u.id, 'name': u.name})
    return json.dumps({'elements': array, 'page': p, 'max_page': max_page, 'count': count})

@app.route('/api/following',  methods=['GET'])
def api_following():
    log.write("following has been called")
    userId = request.args.get('userId', '')
    if not userId:
        log.write("following return an error", 1)
        return jsonify(error='1')

    p = int(request.args.get('p', config.DEFAULT_PAGE))
    pp = int(request.args.get('pp', config.DEFAULT_PER_PAGE))
    count = Subscribes.query.filter_by(userId=userId).count()
    
    p, pp, max_page = pagination(p, pp, count)
    following = Subscribes.query.filter_by(userId=userId).offset((p-1)*pp).limit(pp).all()
    users = db.session.query(Users.id, Users.name).filter(Users.id.in_(tuple(f.subId for f in following))).all()
    array = []
    for u in users:
        array.append({'userId': u.id, 'name': u.name})
    return json.dumps({'elements': array, 'page': p, 'max_page': max_page, 'count': count})


def get_follow(userId, subId):
    follow = Subscribes.query.filter_by(userId=userId, subId=subId).first()
    follower = Subscribes.query.filter_by(userId=subId, subId=userId).first()
    isFollow = False
    isFollower = False
    if follow:
        isFollow = True
    if follower:
        isFollower = True
    return jsonify(isFollow=isFollow, isFollower=isFollower)

@app.route('/api/rest_subscribe',  methods=['GET', 'POST', 'DELETE'])
def rest_subscribe():
    log.write("{method} rest_subscribe has been called".format(method=request.method))
    if request.method == 'GET':
        userId = request.args.get('userId', '')
        subId = request.args.get('subId', '')
        user = Users.query.filter_by(id=userId).first()
        sub = Users.query.filter_by(id=subId).first()
        if user and sub:
            return get_follow(userId,subId)
    if request.method == 'POST':
        userId = request.args.get('userId', '')
        subId = request.args.get('subId', '')
        user = Users.query.filter_by(id=userId).first()
        sub = Users.query.filter_by(id=subId).first()
        if user and sub:
            if userId == subId:
                log.write("userId is equal to subId", 2)
            else:
                s = Subscribes(userId=userId, subId=subId)
                db.session.add(s)
                db.session.commit()
                return get_follow(userId, subId)
    if request.method == 'DELETE':
        userId = request.args.get('userId', '')
        subId = request.args.get('subId', '')
        user = Users.query.filter_by(id=userId).first()
        sub = Users.query.filter_by(id=subId).first()
        if user and sub:
            if userId == subId:
                log.write("userId is equal to subId", 2)
            else:
                s = Subscribes.query.filter_by(userId=userId, subId=subId).first()
                if s:
                    db.session.delete(s)
                    db.session.commit()
                    return get_follow(userId, subId)
    log.write("{method} rest_user return an error".format(method=request.method), 1)
    return jsonify(error='1')

@app.route('/api/rest_user',  methods=['GET', 'POST', 'PUT', 'DELETE'])
def rest_user():
    log.write("{method} rest_user has been called".format(method=request.method))
    if request.method == 'GET':
        userId = request.args.get('userId', '')
        user = Users.query.filter_by(id=userId).first()
        if user:
            followers = Subscribes.query.filter_by(subId=userId).count()
            following = Subscribes.query.filter_by(userId=userId).count()
            return jsonify(id=user.id, name=user.name, followers=followers, following=following)
    if request.method == 'POST':
        login = request.args.get('login', '')
        pas = request.args.get('pas', '')
        mail = request.args.get('mail', '')
        name = request.args.get('name', '')
        registrationTime = datetime.utcnow()

        user = LoginPas.query.filter_by(login=login).first()
        testm = Users.query.filter_by(mail=mail).first()
        if not (user or testm) and pas and mail and name: # pas check
            user = Users(name=name, mail=mail, registrationTime=registrationTime)
            db.session.add(user)
            db.session.commit()
            user = Users.query.filter_by(mail=mail).first()
            lp = LoginPas(userId=user.id, login=login, password=pas)
            db.session.add(lp)
            db.session.commit()
            return jsonify(id=user.id, name=user.name, mail=user.mail)
    if request.method == 'PUT':
        userId = request.args.get('userId', '')
        mail = request.args.get('mail', '')
        name = request.args.get('name', '')
        newpas = request.args.get('newpas', '')
        oldpas = request.args.get('oldpas', '')
        user = Users.query.filter_by(id=userId).first()
        if user:
            if name:
                Users.query.filter_by(id=userId).update({'name': name})
            if mail:
                testm = Users.query.filter_by(mail=mail).first()
                if not testm:
                    Users.query.filter_by(id=userId).update({'mail': mail})
            db.session.commit()
            pasChanged = False
            if newpas and oldpas:
                lp = LoginPas.query.filter_by(userId=userId).first()
                if lp and oldpas == lp.password:
                    LoginPas.query.filter_by(userId=userId).update({'password': newpas})
                    db.session.commit()
                    pasChanged = True
            user = Users.query.filter_by(id=userId).first()
            return jsonify(id=user.id, name=user.name, mail=user.mail, pasChanged=pasChanged)
    if request.method == 'DELETE':
        userId = request.args.get('userId', '')
        user = Users.query.filter_by(id=userId).first()
        if user:
            a = Users.query.filter_by(id=userId).first()
            db.session.delete(a)
            db.session.commit()
            return jsonify(answer='Success')
    log.write("{method} rest_user return an error".format(method=request.method), 1)
    return jsonify(error='1')


if __name__ == '__main__':
    assert len(sys.argv) == 6, "Front needs services ports"
    config.load_config(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    app.run(host='localhost', port=config.USERS_PORT, debug=True)
