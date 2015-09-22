# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider
from logger import Logger
import urllib, urllib2, json, math
from config import Config
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

log = Logger("test_log.txt", "Test")
config = Config()

app = Flask(__name__)
app.debug = True

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

# test session
@app.route('/api/session_get',  methods=['GET'])
def session_get():
    url = 'http://localhost:{port}/api/rest_session?sid={sid}'.format(port=config.SESSION_PORT,sid='Xnm')
    a, error = getJSONdata(url, 'GET', 'session_get')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/session_post',  methods=['GET'])
def session_post():
    url = 'http://localhost:{port}/api/rest_session?userId={userId}'.format(port=config.SESSION_PORT,userId=1)
    a, error = getJSONdata(url, 'POST', 'session_post')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/session_put',  methods=['GET'])
def session_put():
    url = 'http://localhost:{port}/api/rest_session?sid={sid}'.format(port=config.SESSION_PORT,sid='Xnm')
    a, error = getJSONdata(url, 'PUT', 'session_put')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/session_delete',  methods=['GET'])
def session_delete():
    url = 'http://localhost:{port}/api/rest_session?sid={sid}'.format(port=config.SESSION_PORT,sid='ilu')
    a, error = getJSONdata(url, 'DELETE', 'session_delete')
    if not error:
        return jsonify(a)
    else:
        return "fail"


# test users
@app.route('/api/user_get',  methods=['GET'])
def rest_user_get():
    url = 'http://localhost:{port}/api/rest_user?userId={uid}'.format(port=config.USERS_PORT,uid=1)
    a, error = getJSONdata(url, 'GET', 'rest_user_get')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/user_post',  methods=['GET'])
def rest_user_post():
    url = 'http://localhost:{port}/api/rest_user?login={login}&pas={pas}&mail={mail}&name={name}'.format(port=config.USERS_PORT,login='dark',pas='1234',mail='dy',name='valik')
    a, error = getJSONdata(url, 'POST', 'user_post')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/user_put',  methods=['GET'])
def rest_user_put():
    url = 'http://localhost:{port}/api/rest_user?userId={uid}&mail={mail}&name={name}&newpas={newpas}&oldpas={oldpas}'.format(port=config.USERS_PORT,uid=3,mail='14',name='88',newpas='2',oldpas='1234')
    a, error = getJSONdata(url, 'PUT', 'user_put')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/user_delete',  methods=['GET'])
def rest_user_delete():
    url = 'http://localhost:{port}/api/rest_user?userId={uid}'.format(port=config.USERS_PORT,uid=3)
    a, error = getJSONdata(url, 'DELETE', 'user_delete')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/subscribe_get',  methods=['GET'])
def rest_subscribe_get():
    url = 'http://localhost:{port}/api/rest_subscribe?userId={uid}&subId={sid}'.format(port=config.USERS_PORT,uid=1,sid=3)
    a, error = getJSONdata(url, 'GET', 'subscribe_get')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/subscribe_post',  methods=['GET'])
def rest_subscribe_post():
    url = 'http://localhost:{port}/api/rest_subscribe?userId={uid}&subId={sid}'.format(port=config.USERS_PORT,uid=1,sid=3)
    a, error = getJSONdata(url, 'POST', 'subscribe_post')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/subscribe_delete',  methods=['GET'])
def rest_subscribe_delte():
    url = 'http://localhost:{port}/api/rest_subscribe?userId={uid}&subId={sid}'.format(port=config.USERS_PORT,uid=1,sid=3)
    a, error = getJSONdata(url, 'DELETE', 'subscribe_delete')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/user_access',  methods=['GET'])
def user_access():
    url = 'http://localhost:{port}/api/user_access?userId={uid}'.format(port=config.USERS_PORT,uid=3)
    a, error = getJSONdata(url, 'GET', 'user_access')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/user_by_login',  methods=['GET'])
def user_by_login():
    url = 'http://localhost:{port}/api/user_by_login?login={login}&pas={pas}'.format(port=config.USERS_PORT,login='dark',pas='2')
    a, error = getJSONdata(url, 'GET', 'user_by_login')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/followers',  methods=['GET'])
def followers():
    url = 'http://localhost:{port}/api/followers?userId={uid}'.format(port=config.USERS_PORT,uid='1')
    a, error = getJSONdata(url, 'GET', 'followers')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/following',  methods=['GET'])
def following():
    url = 'http://localhost:{port}/api/following?userId={uid}'.format(port=config.USERS_PORT,uid='1')
    a, error = getJSONdata(url, 'GET', 'following')
    if not error:
        return jsonify(a)
    else:
        return "fail"
    
@app.route('/api/user_feed',  methods=['GET'])
def user_feed():
    url = 'http://localhost:{port}/api/user_feed?userId={uid}'.format(port=config.FEED_PORT,uid='2')
    a, error = getJSONdata(url, 'GET', 'user_feed')
    if not error:
        return jsonify(a)
    else:
        return "fail"
    
@app.route('/api/rest_feed_get',  methods=['GET'])
def rest_feed_get():
    url = 'http://localhost:{port}/api/rest_feed?userId={uid}'.format(port=config.FEED_PORT,uid='1')
    a, error = getJSONdata(url, 'GET', 'rest_feed_get')
    if not error:
        return jsonify(a)
    else:
        return "fail"
    
@app.route('/api/rest_feed_post',  methods=['GET'])
def rest_feed_post():
    url = 'http://localhost:{port}/api/rest_feed?userId={uid}&isRepost={isRepost}'.format(port=config.FEED_PORT,uid='2',isRepost='0')
    values = { 'note': 'Please work #Afftar #vypiy #yadu' }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    resp = urllib2.urlopen(req)
    answ = json.loads(resp.read())
    if not ('error' in answ):
        return jsonify(answ)
    else:
        return "fail"

@app.route('/api/rest_feed_repost',  methods=['GET'])
def rest_feed_repost():
    url = 'http://localhost:{port}/api/rest_feed?userId={uid}&isRepost={isRepost}&repostId={repostId}'.format(port=config.FEED_PORT,uid='1',isRepost='1',repostId='3')
    a, error = getJSONdata(url, 'POST', 'rest_feed_repost')
    if not error:
        return jsonify(a)
    else:
        return "fail"
 
@app.route('/api/rest_feed_delete',  methods=['GET'])
def rest_feed_delete():
    url = 'http://localhost:{port}/api/rest_feed?noteId={nid}'.format(port=config.FEED_PORT,nid='6') # 1
    a, error = getJSONdata(url, 'DELETE', 'rest_feed_delete')
    if not error:
        return jsonify(a)
    else:
        return "fail"

@app.route('/api/search_tag',  methods=['GET'])
def search_tag():
    url = 'http://localhost:{port}/api/search_tag?keyword={keyword}'.format(port=config.SEARCH_PORT,keyword='afftar') # 1
    a, error = getJSONdata(url, 'GET', 'search_tag')
    if not error:
        return jsonify(a)
    else:
        return "fail"
    
@app.route('/api/search_user',  methods=['GET'])
def search_user():
    url = 'http://localhost:{port}/api/search_user?keyword={keyword}'.format(port=config.SEARCH_PORT,keyword='valik') # 1
    a, error = getJSONdata(url, 'GET', 'search_user')
    if not error:
        return jsonify(a)
    else:
        return "fail"




if __name__ == '__main__':
    app.run(host='localhost', port=config.TEST_PORT, debug=True)
