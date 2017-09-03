#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, FileField, RadioField
from wtforms import SelectField, HiddenField, BooleanField, PasswordField, DateTimeField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import Required, ValidationError, Email, Length, Regexp, EqualTo


from ..models import *

from wtforms.validators import Required, ValidationError


choices=[('4:0','4:0'),
	('4:1','4:1'),
	('4:2','4:2'),
	('4:3','4:3'),
	('3:4','3:4'),
	('2:4','2:4'),
	('1:4','1:4'),
	('0:4','0:4')]

class PredictionForm(Form):
        
    answer = SelectField(u'Odgovor(i)', choices=choices,
    	coerce=unicode,validators=[Required()])
    submit = SubmitField(u'Unesi prognozu')

    
class SeriesForm(Form):
       
    home = StringField(u'Home',validators=[Required()])
    away = StringField(u'Away',validators=[Required()])
    
    submit = SubmitField(u'Unesi seriju')

class CloseForm(Form):
       
   
    submit = SubmitField(u'Zatvori predviđanja')


class CommentForm(Form):
       
    body = TextAreaField(u'Komentar',validators=[Required(), Length(1,200)])
        
    submit = SubmitField(u'Komentar')