from datetime import datetime, timedelta
from flask import Flask
from flask import session, request
from flask import render_template, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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
Notes = fullDB['Notes']
Tags = fullDB['Tags']

log = Logger("search_log.txt", "Search")

#REST

def pagination(p, pp, count):
    if pp <= 0:
        pp = count
        max_page = 1
    else:
        max_page = int(math.ceil(count * 1.0 / pp))
        
    if (p < 1) or (p > max_page):
        p = max_page

    return p, pp, max_page


@app.route('/api/search_tag',  methods=['GET'])
def search_tag():
    log.write("{method} search has been called".format(method=request.method))
    keyword = request.args.get('keyword', '')
    p = int(request.args.get('p', config.DEFAULT_PAGE))
    pp = int(request.args.get('pp', config.DEFAULT_PER_PAGE))
    count = db.session.query(Tags.noteId).filter(func.lower(Tags.tagName)==func.lower(keyword)).count()

    p, pp, max_page = pagination(p, pp, count)
    notesId = db.session.query(Tags.noteId).filter(func.lower(Tags.tagName)==func.lower(keyword)).offset((p-1)*pp).limit(pp).all()
    
    ids = []
    for x in notesId:
        ids.append(x[0])
    notes = Notes.query.filter(Notes.id.in_(ids)).join(Users, Users.id==Notes.userId).add_columns(Users.name, Notes.userId, Notes.note, Notes.repost, Notes.repostId, Notes.repostCount).all()

    array = []
    for n in notes:
        array.append({'userId': n.userId, 'name': n.name, 'note': n.note, 'isRepost': n.repost, 'repostCount': n.repostCount})

    return json.dumps({'elements': array, 'page': p, 'max_page': max_page, 'count': count})    

@app.route('/api/search_user',  methods=['GET'])
def search():
    log.write("{method} search has been called".format(method=request.method))
    keyword = request.args.get('keyword', '')
    p = int(request.args.get('p', config.DEFAULT_PAGE))
    pp = int(request.args.get('pp', config.DEFAULT_PER_PAGE))
    count = Users.query.filter(func.lower(Users.name)==func.lower(keyword)).count()

    p, pp, max_page = pagination(p, pp, count)
    users = Users.query.filter_by(name=keyword).offset((p-1)*pp).limit(pp).all()
    
    array = []
    for u in users:
        array.append({'id': u.id, 'name': u.name})

    return json.dumps({'elements': array, 'page': p, 'max_page': max_page, 'count': count})    

if __name__ == '__main__':
    app.run(host='localhost', port=config.SEARCH_PORT, debug=True)
