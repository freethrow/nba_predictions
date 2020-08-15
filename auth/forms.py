#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email
from wtforms.validators import Required, ValidationError, Email, Length, Regexp, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from slugify import slugify
from ..models import User

def all_users():

    return User.query.all()

class LoginForm(Form):
    username = StringField(u'Username', validators=[Required(), Length(4,20)])
    password = PasswordField(u'Password', validators=[Required(),Length(4,20)])
    remember_me = BooleanField(u'Ostani ulogovan')
    submit = SubmitField(u'Uloguj me')




class RegisterForm(Form):
    #username = StringField(u'Username', validators=[Required(), Length(4,20)])

    username = StringField(u'Korisničko ime', validators=[
        Required(), Length(4, 20), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          u'Korisničko ime može sadržati slova, brojeve, _ i .'
                                          )])


    password = PasswordField(u'Šifra', validators=[Required(),Length(4,20)])
    password2 = PasswordField(u'Šifra (ponovo)', validators=[
        Required(), EqualTo('password', message=u'Šifre moraju da budu iste.'),Length(4, 20)])
    submit = SubmitField(u'Napravi nalog')


    def validate_username(self, field):

        if User.query.filter_by(username=field.data).first():
            print "Already"
            raise ValidationError(u'Ovo korisničko ime je već zauzeto.')


class SetPassForm(Form):
    username = QuerySelectField(u'Username?',query_factory=all_users)
    new_pass = StringField(u'New password', validators=[Required(),Length(4,20)])

    submit = SubmitField(u'Izmeni pass')