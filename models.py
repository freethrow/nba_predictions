#!/usr/bin/python
# -*- coding: utf-8 -*-


# models.py
from flask import current_app, request, url_for
from datetime import datetime
import hashlib
from slugify import slugify

from flask_sqlalchemy import SQLAlchemy, orm

from flask_login import UserMixin, AnonymousUserMixin

from sqlalchemy.sql import func

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeSerializer
from . import db, login_manager



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



##############################################################
class User(UserMixin, db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    #email = db.Column(db.String(64), unique = True, index = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean(),default=False)
    score = db.Column(db.Integer(),default=0)



    @property
    def password(self):

        raise AttributeError('password not readable')

    @property
    def total(self):

        total=0
        user_preds = Prediction.query.filter(
            Prediction.user==self).all()

        for predict in user_preds:
            if predict.score_made:
                total+=int(predict.score_made)

        return total


    @password.setter
    def password(self,password):

        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except AttributeError:
            return False


    def __repr__(self):
        return unicode(self.username)


    @staticmethod
    def generate_fake(count=20):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randrange, randint
        import forgery_py

        seed()
        for i in range(count):
            u = User(username=forgery_py.internet.user_name(True))
            u.password = u.username
            u.score=randint(0,120)
            db.session.add(u)
            try:
                db.session.commit()
                print "Dodat korisnik ",u.username
            except IntegrityError:
                db.session.rollback()


class Series(db.Model):

    __tablename__ = 'series'

    id = db.Column(db.Integer, primary_key = True)

    home = db.Column(db.Text)
    away = db.Column(db.Text)
    open = db.Column(db.Boolean, default = True)
    result = db.Column(db.String)




    def __repr__(self):

        return u"Series {0} - {1}".format(self.home, self.away)




class Prediction(db.Model):

    __tablename__ = 'predictions'


    id = db.Column(db.Integer, primary_key = True)

    series_id = db.Column(db.Integer, db.ForeignKey('series.id'))
    series = db.relationship('Series',  foreign_keys=[series_id])

    created = db.Column(db.DateTime(), default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User',  foreign_keys=[user_id])

    predicted = db.Column(db.String)
    score_made = db.Column(db.Integer(),default=0)






    __table_args__ = (
        db.UniqueConstraint(series_id, user_id),
    )



    def __repr__(self):

        return u"Prediction for series {0} for user {1}-->{2}".format(self.series, self.user, self.predicted)

class Comment(db.Model):

    __tablename__ = 'comments'


    id = db.Column(db.Integer, primary_key = True)

    created = db.Column(db.DateTime(), default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User',  foreign_keys=[user_id])

    body = db.Column(db.Text())

    def __repr__(self):

    	return 'Comment {0} from {1}'.format(self.body, self.user.username)



def calculate_score(pred, actual):



    pred_home = int(pred.split(':')[0])
    pred_away = int(pred.split(':')[1])

    actual_home = int(actual.split(':')[0])
    actual_away = int(actual.split(':')[1])

    score = 0


    # the 15 points for the overall winner
    if (pred_home-pred_away)*(actual_home-actual_away)>0:
        score+=15

        diff = abs(min(pred_home, pred_away)-min(actual_home,actual_away))
        print diff
        if (diff == 0):
            score+=10

        if (diff == 1):
            score+=5

        if (diff==2):
            score+=2

        if (actual_home-actual_away)<0:
            score+=1


    return score



