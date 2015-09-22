# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from flask import Flask
from flask import session, request, url_for
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import gen_salt
import urllib, urllib2, base64, json
import json, math, sys
from config import Config
from logger import Logger

reload(sys)  
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.debug = True
app.secret_key = 'secret'

log = Logger("front_log.txt", "Front")
config = Config()

log.write(sys.argv)
assert len(sys.argv) == 6, "Front needs services ports"
config.load_config(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))

# need to update session
# check notation
# bad code, a lot of copypaste, should be more clear 
# I should spend more time on this, but this is for study and I don't get any money for this

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

def update_session():
    if 'sid' in session:
        url = 'http://localhost:{port}/api/rest_session?sid={sid}'.format(port=config.SESSION_PORT,sid=session['sid'])
        a, error = getJSONdata(url, 'PUT', 'session_put')
        if 'error' in answ:
            return (error_handler(answ), 1)
        session['sid'] = a['sid']
    return (answ, 0)

def delete_session(sid):
    url = 'http://localhost:{port}/api/rest_session?sid={sid}'.format(port=config.SESSION_PORT,sid=sid)
    answ, error = getJSONdata(url, 'DELETE', 'delete_session')
    if 'error' in answ:
        return (error_handler(answ), 1)
    return (answ, 0)

def error_handler(msg):  
    if msg['error'] == '0':
        if 'sid' in session:
            delete_session(session['sid'])
            session.clear()
        return 'Authorization error. Your session will be cleared.'
    if msg['error'] == '1':
        return 'Internal service error'
    if msg['error'] == '2':
        return msg['error_message']
    return 'Unknow error'

def get_user(sid):
    url = 'http://localhost:{port}/api/rest_session?sid={sid}'.format(port=config.SESSION_PORT, sid=sid)
    answ, error = getJSONdata(url, 'GET', 'get_user')
    if error:
        return (error_handler(answ), 1)
    return (answ, 0)

def get_user_by_login(login, pas):
    url = 'http://localhost:{port}/api/user_by_login?login={login}&pas={pas}'.format(port=config.USERS_PORT,login=login,pas=pas)
    answ, error = getJSONdata(url, 'GET', 'get_user_by_login')
    if error:
        return (error_handler(answ), 1)
    url = 'http://localhost:{port}/api/rest_session?userId={userId}'.format(port=config.SESSION_PORT,userId=answ['userId'])
    answ, error = getJSONdata(url, 'POST', 'get_user_by_login')
    if error:
        return (error_handler(answ), 1)
    session['sid'] = answ['sid']
    answ, error = get_user(session['sid']) 
    return (answ, error)


# def get_status(request, Authorize?) return data for template
def getStatus():
    if 'sid' in session:
        user, error = get_user(session['sid'])
        if error:
            return None, {'redirectToIndexButton': True}
        url = 'http://localhost:{port}/api/rest_user?userId={uid}'.format(port=config.USERS_PORT,uid=user['id'])
        user, error = getJSONdata(url, 'GET', 'get_user_menu')
        if error:
            return None, {'redirectToIndexButton': True, 'searchUserButton': True, 'searchTagButton': True}
        curId = user['id']
        return curId, {'name': user['name'], 'exitButton': True, 'tweetButton': True, 'homeButton': True, 'searchUserButton': True, 'searchTagButton': True}
    return None, {'redirectToIndexButton': True, 'searchUserButton': True, 'searchTagButton': True}

# should be safe
# def user_menu(request, or sid) return data for template
def get_user_menu(userId=None, curId=None):
    log.write("get_user_menu was called")
    if not userId:
        userId = curId
    if userId:
        url = 'http://localhost:{port}/api/rest_user?userId={uid}'.format(port=config.USERS_PORT,uid=userId)
        user, error = getJSONdata(url, 'GET', 'get_user_menu')
        if error:
           return None
        if curId and int(userId) != int(curId):
            url = 'http://localhost:{port}/api/rest_subscribe?userId={uid}&subId={sid}'.format(port=config.USERS_PORT,uid=curId,sid=userId)
            ff, error = getJSONdata(url, 'GET', 'get_user_menu')
            if error:
                return None
            return {'userId': user['id'], 'isFollow': ff['isFollow'], 'isFollower': ff['isFollower'], 'followers': user['followers'], 'following': user['following'], 'name': user['name']}
        return {'userId': user['id'], 'followers': user['followers'], 'following': user['following'], 'name': user['name']}
    return None

def get_feed(userId=None, curId=None, p=1, pp=10):
    log.write("get_feed was called")
    if not userId:
        userId = curId
    if userId:
        if curId and int(userId) == int(curId):
            url = 'http://localhost:{port}/api/rest_feed?userId={uid}&p={p}&pp={pp}'.format(port=config.FEED_PORT,uid=userId,p=p,pp=pp)
            answ, error = getJSONdata(url, 'GET', 'get_feed')
            if error:
                return None
            return answ
        else:
            url = 'http://localhost:{port}/api/user_feed?userId={uid}&p={p}&pp={pp}'.format(port=config.FEED_PORT,uid=userId,p=p,pp=pp)
            answ, error = getJSONdata(url, 'GET', 'user_feed')
            if error:
                return None
            return answ
    return None

def genPages(p, maxPage):
    array = []
    for i in range(1, 4):
        if i <= maxPage:
            array.append(i)
    for i in range(p-2, p+3):
        if i <= maxPage and i > 0:
            array.append(i)
    for i in range(maxPage-2, maxPage+1):
        if i <= maxPage and i > 0:
            array.append(i)
    return set(array)

# title / index / login
@app.route('/index', methods=('GET', 'POST'))
def index():
    log.write("index was called")
    if 'sid' in session:
        data, error = get_user(session['sid'])
        if error:
            return render_template('title.html', msg=data)
        return redirect('main')
    return render_template('title.html')

@app.route('/', methods=('GET', 'POST'))
def title():
    return redirect('index')

@app.route('/exit')
def uexit():
    if 'sid' in session:
        delete_session(session['sid'])
        session.clear()
    return redirect('/')

# /user?id=login
@app.route('/main', methods=('GET', 'POST'))
def main():
    # build page
    # push all this data to page
    log.write("{method} main has been called".format(method=request.method))
    userId = request.args.get('userId', None)
    p = request.args.get('p', 1)
    pp = request.args.get('pp', 10)
    curId, status = getStatus()

    menuData = get_user_menu(userId, curId)

    if not menuData:
        return redirect('index') # or msg
        
    if userId and curId and int(userId) != int(curId):
        if menuData['isFollow']:
            menuData['unsubscribeButton'] = True
        else:
            menuData['subscribeButton'] = True
    elif curId:
        menuData['settingsButton'] = True

    feed = get_feed(userId, curId, p, pp)
    # work with feed
    
    if curId and (curId==userId):
        update_session()
    
    log.write(status)
    log.write(menuData)
    log.write(feed)

    maxPage = int(feed['max_page'])
    p = int(feed['page'])
    pages = genPages(p, maxPage)
    
    return render_template('main.html', status=status, menuData=menuData, feed=feed, p=p, pp=pp, pages=pages, curId=curId, userId=userId, 
                           feedLink=url_for('main'), followingLink=url_for('following'), followerLink=url_for('followers'))

@app.route('/following', methods=('GET', 'POST'))
def following():
    log.write("{method} following has been called".format(method=request.method))
    userId = request.args.get('userId', None)
    p = request.args.get('p', 1)
    pp = request.args.get('pp', 10)
    curId, status = getStatus()

    menuData = get_user_menu(userId, curId)

    if not menuData:
        return redirect('index') # or msg
        
    if userId and curId and int(userId) != int(curId):
        if menuData['isFollow']:
            menuData['unsubscribeButton'] = True
        else:
            menuData['subscribeButton'] = True
    elif curId:
        menuData['settingsButton'] = True

    url = 'http://localhost:{port}/api/following?userId={uid}&p={p}&pp={pp}'.format(port=config.USERS_PORT,uid=userId,p=p,pp=pp)
    answ, error = getJSONdata(url, 'GET', 'following')
    if error:
        return redirect('index') # or msg
    # work with feed
    
    log.write(status)
    log.write(menuData)
    log.write(answ)

    maxPage = int(answ['max_page'])
    p = int(answ['page'])
    pages = genPages(p, maxPage)
    return render_template('follow.html', follow="following", status=status, menuData=menuData, users=answ, p=p, pp=pp, pages=pages, curId=curId, userId=userId, 
                           feedLink=url_for('main'), followingLink=url_for('following'), followerLink=url_for('followers'))

@app.route('/followers', methods=('GET', 'POST'))
def followers():
    log.write("{method} following has been called".format(method=request.method))
    userId = request.args.get('userId', None)
    p = request.args.get('p', 1)
    pp = request.args.get('pp', 10)
    curId, status = getStatus()

    menuData = get_user_menu(userId, curId)

    if not menuData:
        return redirect('index')
        
    if userId and curId and int(userId) != int(curId):
        if menuData['isFollow']:
            menuData['unsubscribeButton'] = True
        else:
            menuData['subscribeButton'] = True
    elif curId:
        menuData['settingsButton'] = True

    url = 'http://localhost:{port}/api/followers?userId={uid}&p={p}&pp={pp}'.format(port=config.USERS_PORT,uid=userId,p=p,pp=pp)
    answ, error = getJSONdata(url, 'GET', 'followers')
    if error:
        return redirect('index')

    log.write(status)
    log.write(menuData)
    log.write(answ)

    maxPage = int(answ['max_page'])
    p = int(answ['page'])
    pages = genPages(p, maxPage)
    return render_template('follow.html', follow="follower", status=status, menuData=menuData, users=answ, p=p, pp=pp, pages=pages, curId=curId, userId=userId, 
                           feedLink=url_for('main'), followingLink=url_for('following'), followerLink=url_for('followers'))

@app.route('/subscribe', methods=('GET', 'POST'))
def subscribe():
    log.write("{method} subscribe has been called".format(method=request.method))
    if request.method=='POST':
        userId = request.form.get('userId', None)
        if not userId:
            return redirect('main')

        curId, status = getStatus()
        if not curId or int(curId)==int(userId):
            log.write("{method} subscribe return an error".format(method=request.method))
            return redirect('main')

        url = 'http://localhost:{port}/api/rest_subscribe?userId={uid}&subId={sid}'.format(port=config.USERS_PORT,uid=curId,sid=userId)
        a, error = getJSONdata(url, 'POST', 'subscribe')
        if error:
            log.write("{method} subscribe return an error".format(method=request.method))
    return redirect(url_for('main', userId=userId))

@app.route('/unsubscribe', methods=('GET', 'POST'))
def unsubscribe():
    log.write("{method} unsubscribe has been called".format(method=request.method))
    if request.method=='POST':
        userId = request.form.get('userId', None)
        if not userId:
            return redirect('main')

        curId, status = getStatus()
        if not curId or int(curId)==int(userId):
            log.write("{method} unsubscribe return an error".format(method=request.method))
            return redirect('main')

        url = 'http://localhost:{port}/api/rest_subscribe?userId={uid}&subId={sid}'.format(port=config.USERS_PORT,uid=curId,sid=userId)
        a, error = getJSONdata(url, 'DELETE', 'unsubscribe')
        if error:
            log.write("{method} unsubscribe return an error".format(method=request.method))
    return redirect(url_for('main', userId=userId))

@app.route('/settings', methods=('GET', 'POST'))
def settings():
    if request.method=='GET':
        curId, status = getStatus()
        if not curId:
            log.write("{method} settings return an error".format(method=request.method))
            return redirect('main')

        url = 'http://localhost:{port}/api/user_access?userId={uid}'.format(port=config.USERS_PORT,uid=curId)
        data, error = getJSONdata(url, 'GET', 'user_access')
        if error:
            return render_template('settings.html', status=status, name=None, email=None, msg=data)
        return render_template('settings.html', status=status, name=data['name'], email=data['mail'])
    if request.method=='POST':
        curId, status = getStatus() 
        if not curId:
            log.write("{method} settings return an error".format(method=request.method))
            return redirect('main')

        oldPas = request.form.get('oldPas', None)
        newPas = request.form.get('newPas', None)
        name = request.form.get('name', None)
        mail = request.form.get('mail', None)
        
        url = 'http://localhost:{port}/api/rest_user?userId={uid}&mail={mail}&name={name}&newpas={newpas}&oldpas={oldpas}'.format(port=config.USERS_PORT,uid=curId,mail=mail,name=name,newpas=newPas,oldpas=oldPas)
        data, error = getJSONdata(url, 'PUT', 'settings')
        if error:
            return render_template('settings.html', status=status, name=None, email=None, msg=error_handler(data))
        
        msg = None
        if newPas and not data['pasChanged']:
            msg = "Password wasn't changed"
        return render_template('settings.html', status=status, name=data['name'], email=data['mail'], msg=msg)
    return redirect('main')

#feed
@app.route('/write', methods=('GET', 'POST'))
def write():
    if request.method=='GET':
        curId, status = getStatus()
        if not curId:
            log.write("{method} tweet return an error".format(method=request.method))
            return redirect('main')

        url = 'http://localhost:{port}/api/user_access?userId={uid}'.format(port=config.USERS_PORT,uid=curId)
        data, error = getJSONdata(url, 'GET', 'user_access')
        if error:
            return render_template('write.html', status=status)
        return render_template('write.html', status=status, name=data['name'], email=data['mail'])
    if request.method=='POST':
        curId, status = getStatus() 
        if not curId:
            log.write("{method} settings return an error".format(method=request.method))
            return redirect('main')

        values = request.form.get('note', None)
        log.write(values)
        if not values:
            return render_template('write.html', msg="empty message")
        
        if len(values)>config.MESSAGE_LENGTH:
            return render_template('write.html', msg="length of message can't be more 140 symbols")

        url = 'http://localhost:{port}/api/rest_feed?userId={uid}&isRepost={isRepost}'.format(port=config.FEED_PORT,uid=curId,isRepost='0')
        data = urllib.urlencode({'note': values})
        req = urllib2.Request(url, data)
        resp = urllib2.urlopen(req)
        answ = json.loads(resp.read())
        log.write(answ)
        if 'error' in answ:
            return render_template('write.html', msg=error_handler(answ))
    return redirect('main')

# get - return form to write
# post - add tweet and redirect

@app.route('/retweet', methods=('GET', 'POST'))
def retweet():
    log.write("{method} retweet has been called".format(method=request.method))
    if request.method=='POST':
        tweetId = int(request.form.get('tweetId', None))
        if not tweetId:
            return redirect('main')

        curId, status = getStatus()
        if not curId:
            log.write("{method} retweet return an error".format(method=request.method))
            return redirect('main')

        url = 'http://localhost:{port}/api/rest_feed?userId={uid}&isRepost={isRepost}&repostId={repostId}'.format(port=config.FEED_PORT,uid=curId,isRepost='1',repostId=tweetId)
        a, error = getJSONdata(url, 'POST', 'retweet')
        if error:
            log.write("{method} retweet return an error".format(method=request.method))
    return redirect('main')


@app.route('/delete_tweet', methods=('GET', 'POST'))
def delete_link():
    log.write("{method} delete_tweet has been called".format(method=request.method))
    if request.method=='POST':
        tweetId = int(request.form.get('tweetId', None))
        if not tweetId:
            return redirect('main')
        
        curId, status = getStatus()
        if not curId:
            log.write("{method} delete_tweet return an error".format(method=request.method))
            return redirect('main')

        url = 'http://localhost:{port}/api/rest_feed?noteId={nid}&userId={uid}'.format(port=config.FEED_PORT,nid=tweetId,uid=curId)
        a, error = getJSONdata(url, 'DELETE', 'delete_tweet')
        if error:
            log.write("{method} delete_tweet return an error".format(method=request.method))
    return redirect('index')

# Authorization
@app.route('/login', methods=('GET', 'POST'))
def login():
    log.write("{method} login has been called".format(method=request.method))
    if request.method=='POST':
        login = request.form.get('login')
        pas = request.form.get('pas')
        data, error = get_user_by_login(login, pas)
        log.write(data)
        if error:
            return render_template('title.html', msg=data)
    return redirect('index')

@app.route('/register', methods=('GET', 'POST'))
def register():
    log.write("{method} registration has been called".format(method=request.method))
    login = request.form.get('login')
    pas = request.form.get('pas')
    name = request.form.get('name')
    mail = request.form.get('mail')
    url = 'http://localhost:{port}/api/rest_user?login={login}&pas={pas}&mail={mail}&name={name}'.format(port=config.USERS_PORT,login=login,pas=pas,mail=mail,name=name)
    data, error = getJSONdata(url, 'POST')
    if error:
        log.write("registration return error", 1)
        return render_template('title.html', msg=error_handler(data))
    data, error = get_user_by_login(login, pas)
    if error:
        log.write("registration return error", 1)
        return render_template('title.html', msg=error_handler(data))
    return redirect('index')

@app.route('/search_user', methods=('GET', 'POST'))
def search_user():
    log.write("{method} search_user has been called".format(method=request.method))
    if request.method=='POST':
        keyword = request.form.get('keyword')
        return redirect(url_for('search_user', keyword=keyword))

    keyword = request.args.get('keyword', None)
    p = request.args.get('p', 1)
    pp = request.args.get('pp', 10)
    curId, status = getStatus()

    url = 'http://localhost:{port}/api/search_user?keyword={keyword}'.format(port=config.SEARCH_PORT,keyword=keyword)
    answ, error = getJSONdata(url, 'GET', 'search_user')
    if error:
        return render_template('search.html', search="user", status=status, keyword=keyword, feedLink=url_for('main'), searchLink=url_for('search_user'))
    
    log.write(answ)
    
    maxPage = int(answ['max_page'])
    p = int(answ['page'])
    pages = genPages(p, maxPage)
    return render_template('search.html', search="user", status=status, keyword=keyword, users=answ, p=p, pp=pp, pages=pages, 
                           feedLink=url_for('main'), searchLink=url_for('search_user'))

@app.route('/search_tag', methods=('GET', 'POST'))
def search_tag():
    log.write("{method} search_tag has been called".format(method=request.method))
    if request.method=='POST':
        keyword = request.form.get('keyword', None)
        return redirect(url_for('search_tag', keyword=keyword))

    keyword = request.args.get('keyword', None)
    p = request.args.get('p', 1)
    pp = request.args.get('pp', 10)
    curId, status = getStatus()

    url = 'http://localhost:{port}/api/search_tag?keyword={keyword}'.format(port=config.SEARCH_PORT,keyword=keyword)
    answ, error = getJSONdata(url, 'GET', 'search_tag')
    if error:
        return render_template('search.html', search="tag", status=status, keyword=keyword, feedLink=url_for('main'), searchLink=url_for('search_tag'), curId=curId)
    
    log.write(answ)
    
    maxPage = int(answ['max_page'])
    p = int(answ['page'])
    pages = genPages(p, maxPage)
    return render_template('search.html', search="tag", status=status, keyword=keyword, feed=answ, p=p, pp=pp, pages=pages, 
                           feedLink=url_for('main'), searchLink=url_for('search_tag'), curId=curId)

@app.route('/delete_account', methods=('GET', 'POST'))
def delete_account():
    log.write("{method} delete_account has been called".format(method=request.method))
    if request.method=='POST':
        curId, status = getStatus()
        if not curId:
            log.write("{method} delete_account return an error".format(method=request.method))
            return redirect('main')

        url = 'http://localhost:{port}/api/rest_user?userId={uid}'.format(port=config.USERS_PORT,uid=curId)
        a, error = getJSONdata(url, 'DELETE', 'user_delete')
        if error:
            log.write("{method} delete_tweet return an error".format(method=request.method))
    return redirect('exit')


if __name__ == '__main__':
    log.write(config.FRONT_PORT)
    app.run(host='localhost', port=config.FRONT_PORT, debug=True)