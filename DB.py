from flask_sqlalchemy import SQLAlchemy
from logger import Logger
from sqlalchemy import event
from config import Config

config = Config()

log = Logger("db_log.txt", "DB")

# possible there is a way to get db tables without creating them
def getDB(app):
    db = SQLAlchemy(app)
    
    class Users(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        notes = db.relationship("Notes", cascade="delete")
        session = db.relationship("Session", cascade="delete")
        loginPas = db.relationship("LoginPas", cascade="delete")
        suser = db.relationship('Subscribes', cascade="delete", backref = 'user', lazy = 'dynamic', foreign_keys = 'Subscribes.userId')
        ssub = db.relationship('Subscribes', cascade="delete", backref = 'sub', lazy = 'dynamic', foreign_keys = 'Subscribes.subId')
        name = db.Column(db.String(40))
        mail = db.Column(db.String(60), unique=True, nullable=False)
        registrationTime = db.Column(db.DateTime, nullable=False)
        log.write("Users is created")

    class Session(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        accessToken = db.Column(db.String(255), unique=True, nullable=False)
        #refreshToken = db.Column(db.String(255), unique=True)
        expires = db.Column(db.DateTime, nullable=False)
        log.write("Session is created")

    class LoginPas(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        login = db.Column(db.String(255), unique=True, nullable=False)
        password = db.Column(db.String(255), unique=False, nullable=False)
        log.write("LoginPas is created")

    class Subscribes(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        subId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        log.write("Subscribes is created")

    class Notes(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        userId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        note = db.Column(db.String(config.MESSAGE_LENGTH))
        notes = db.relationship("Notes", cascade="delete")
        tags = db.relationship("Tags", cascade="delete")
        repost = db.Column(db.Boolean, default=False, nullable=False)
        repostId = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=True)
        repostCount = db.Column(db.Integer, default=0, nullable=False)
        registrationTime = db.Column(db.DateTime, nullable=False)
        log.write("Notes is created")

    class Tags(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        tagName = db.Column(db.String(140), nullable=False)
        noteId = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
        log.write("Tags is created")

    def after_insert_note(mapper, connection, target):
        if target.repost:
            r = Notes.query.filter_by(id=target.repostId).first()
            Notes.query.filter_by(id=target.repostId).update({'repostCount': r.repostCount + 1})

    def after_delete_note(mapper, connection, target):
        if target.repost:
            r = Notes.query.filter_by(id=target.repostId).first()
            Notes.query.filter_by(id=target.repostId).update({'repostCount': r.repostCount - 1})

    event.listen(Notes, 'after_insert', after_insert_note)
    event.listen(Notes, 'after_delete', after_delete_note)
    
    return dict({'db': db,
            'Users': Users,
            'Session': Session,
            'LoginPas': LoginPas,
            'Subscribes': Subscribes,
            'Notes': Notes,
            'Tags': Tags })