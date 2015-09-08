from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider
import json, math
import config
from logger import Logger
import DB
import sys  

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
Session = fullDB['Session']

log = Logger("session_log.txt", "Session")

#REST
@app.route('/api/rest_session',  methods=['GET', 'PUT', 'POST', 'DELETE'])
def reg_session():
    log.write("{method} reg_session has been called".format(method=request.method))
    if request.method == 'GET':
        sid = request.args.get('sid', '')
        a = Session.query.filter_by(accessToken=sid).first()
        if a:
            if a.expires > datetime.utcnow():
                return jsonify(id=a.userId, sid=a.accessToken, expires=a.expires)
            else:
                db.session.delete(a)
                db.session.commit()

    if request.method == 'PUT':
        sid = request.args.get('sid', '')
        s = Session.query.filter_by(accessToken=sid).first()
        if s:
            new_sid = gen_salt(config.SALT_LENGTH)
            while Session.query.filter_by(accessToken=new_sid).first() is not None:
                new_sid = gen_salt(config.SALT_LENGTH)
            a = Session.query.filter_by(accessToken=sid).update({
                    'expires': datetime.utcnow() + timedelta(seconds=config.SESSION_EXPIRES),
                    'accessToken': new_sid})
            db.session.commit()
            a = Session.query.filter_by(accessToken=new_sid).first()
            return jsonify(id=a.userId, sid=a.accessToken, expires=a.expires)

    if request.method == 'POST':
        userId = request.args.get('userId', '')
        u = Users.query.filter_by(id=userId).first()
        if u:
            a = Session(userId=u.id, accessToken=gen_salt(config.SALT_LENGTH), expires=datetime.utcnow() + timedelta(seconds=config.SESSION_EXPIRES))
            db.session.add(a)
            db.session.commit()
            return jsonify(id=a.userId, sid=a.accessToken)

    if request.method == 'DELETE':
        sid = request.args.get('sid', '')
        s = Session.query.filter_by(accessToken=sid).first()
        if s:
            db.session.delete(s)
            db.session.commit()
            return jsonify(answer='Success')

    log.write("{method} rest_session return an error".format(method=request.method), 1)
    return jsonify(error='1')

if __name__ == '__main__':
    app.run(host='localhost', port=config.SESSION_PORT, debug=True)
