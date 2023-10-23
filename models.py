from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    '''Connect to database'''
    db.app = app
    db.init_app(app)


class My_Recipes(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False)
    recipe_name = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_favorite = db.Column(db.Boolean, default=False)    

    user = db.relationship('User', backref='recipes')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    # bookmarks = db.relationship('Bookmark', backref='users', lazy=True)

    
    @classmethod
    def register(cls, username, pwd):
        """register user with hashed password and return user"""
        
        hashed = bcrypt.generate_password_hash(pwd)
        #turn bytestring into normal (utf8) string
        hashed_utf8 = hashed.decode('utf8')

        return cls(username=username, password=hashed_utf8)
    
    @classmethod
    def authenticate(cls, username, pwd):
        '''validate that user exists and password is correct
        return id valid else return false'''
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False
        
# class Bookmark(db.Model):
#     __tablename__ = 'bookmarks'

#     id = db.Column(db.Integer, primary_key=True)
#     recipe_uri = db.Column(db.String(255), nullable=False)
#     user_id = db.Column(db.Integer, nullable=False)