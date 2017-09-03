#!/usr/bin/python
# -*- coding: utf-8 -*-


from flask import Flask, render_template, session, redirect, url_for, flash, g, request, make_response, jsonify

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectMultipleField, TextAreaField, FileField, RadioField
from wtforms import SelectField, HiddenField, BooleanField, PasswordField, DateTimeField, DateField

from wtforms import widgets
from .. import db


from flask.ext.login import login_required, login_user, logout_user, current_user
from . import main
from ..models import User, Series, Prediction, calculate_score, Comment
from .forms import PredictionForm,SeriesForm, CommentForm, CloseForm
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user._get_current_object().is_admin:
            flash(u'Samo administrator!')

            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function



@main.route('/', methods=['GET','POST'])
def index():

    
    users = User.query.order_by(User.score.desc()).limit(7)
    # all open series
    open_series = Series.query.filter(Series.open==True).all()

    closed_series = Series.query.filter(Series.open==False).all()


    if current_user.is_authenticated:
        usr = current_user._get_current_object()



        form = CommentForm()  
    
        if form.validate_on_submit():

            comment = Comment()
            comment.body = form.body.data         
            comment.user = usr    
            
            db.session.add(comment)
            

            msg = u'Dodat komentar.'
            flash(msg)

            
            return redirect(url_for('main.index'))
    
        comments = Comment.query.all()

    else:
        form = None
        comments = None

    return render_template('index.html', comments = comments, 
        series = open_series, closed_series = closed_series, users = users, form = form)


@main.route('/predict/<id>', methods=['GET','POST'])
@login_required
def new_prediction(id):

    
    series = Series.query.get_or_404(id)
   
    usr = current_user._get_current_object()

    exists = Prediction.query.filter(
        Prediction.user==usr).filter(
        Prediction.series==series).first()

    if exists:
        preds = Prediction.query.filter(
            Prediction.series==series)
        
        return render_template('main/series.html',
            series = series, preds = preds)

    if not series.open:
        preds = Prediction.query.filter(
            Prediction.series==series)
        
        return render_template('main/series.html',
            series = series, preds = preds, not_open = True)

    if series.result:

        preds = Prediction.query.filter(
            Prediction.series==series)

        msg = u'Serija {0} - {1} je zatvorena, a izgleda da je nisi prognozirao :('.format(
            series.home, series.away)
        flash(msg)
                
        return render_template('main/series.html',
            series = series, preds = preds)
   
    form = PredictionForm()  
    
    if form.validate_on_submit():

        prediction = Prediction()
        prediction.predicted = form.answer.data  
        prediction.series = series
        prediction.user = usr    
        
        db.session.add(prediction)
        

        msg = u'Prognozirao si seriju {0} - {1} da će da se završi rezultatom {2}'.format(
            series.home, series.away, prediction.predicted)
        flash(msg)

        
        return redirect(url_for('main.index'))

        
    return render_template('main/new_prediction.html', form = form, series = series)


@main.route('/series/new', methods=['GET','POST'])
@login_required
@admin_required
def new_series():

    
    form = SeriesForm()  
    
    if form.validate_on_submit():

        series = Series()
        series.home = form.home.data
        series.away = form.away.data
        series.open = True        
        
        db.session.add(series)
        

        msg = u'Uneta nova serija {0} - {1}'.format(
            series.home, series.away)
        flash(msg)

        
        return redirect(url_for('main.index'))

        
    return render_template('main/new_series.html', form = form)






@main.route('/close/<id>', methods=['GET','POST'])
@login_required
@admin_required
def close_series(id):

    
    series = Series.query.get_or_404(id)

    if series.open:
        msg = u'Serija {0} - {1} bi trebalo da je već zatvorena!'.format(
            series.home, series.away)
        flash(msg)
      
    if series.result:
        msg = u'Serija {0} - {1} je već zatvorena rezultatom {2}!'.format(
            series.home, series.away, series.result)
        flash(msg)
        return redirect(url_for('main.index'))

      
    form = PredictionForm()  
    
    if form.validate_on_submit():

        series.result = form.answer.data
        series.open = False
         
        
        db.session.add(series)
        

        msg = u'Zaključio si seriju {0} - {1} rezultatom {2}'.format(
            series.home, series.away, series.result)
        flash(msg)

        # update the users scores
        predicts = Prediction.query.filter(Prediction.series==series).all()
        for pred in predicts:
            # get the score and update it
            user = pred.user
            score = calculate_score(pred.predicted, pred.series.result)
            user_score = user.score
            user.score = user_score+score
            print "Updated user {0}'s score by {1} for series {2}".format(
                user.username, score, pred.series)

            db.session.add(user)
            pred.score_made = calculate_score(pred.predicted, pred.series.result)
            db.session.add(pred)


        
        return redirect(url_for('main.index'))

        
    return render_template('main/close_series.html', form = form, series = series)


# no more predictions - series started

@main.route('/close-preds/<id>', methods=['GET','POST'])
@login_required
@admin_required
def close_preds_series(id):

    
    series = Series.query.get_or_404(id)

    # predictions for the series
    preds = Prediction.query.filter(Prediction.series==series).all()

    if series.open:
        msg = u'Serija {0} - {1} se zatvara za predviđanje!'.format(
            series.home, series.away)
        flash(msg)

     

      
    form = CloseForm()  
    
    if form.validate_on_submit():

        series.open = False         
        
        db.session.add(series)
        

        msg = u'Seriju {0} - {1} je zatvorena za predviđanja'.format(
            series.home, series.away)
        flash(msg)

       

        
        return redirect(url_for('main.index'))

        
    return render_template('main/close_pred_series.html', form = form, series = series, preds = preds)

@main.route('/user/<id>')
@login_required
def user_page(id):

    curr_usr = current_user._get_current_object()

    usr = User.query.get_or_404(id)

    if usr==curr_usr:
        return redirect(url_for('main.my_predictions'))

    #patients = Patient.query.filter(Patient.mother.has(phenoscore=10))

    preds= Prediction.query.filter(
        Prediction.user==usr).filter(Prediction.series.has(Series.open==False)).all()



    return render_template('main/user_page.html', preds=preds, user=usr)



@main.route('/predictions')
@login_required
def my_predictions():

    usr = current_user._get_current_object()
    

    preds= Prediction.query.filter(Prediction.user==usr).all()

        

    return render_template('main/my_preds.html', preds=preds)


@main.route('/scoreboard')
#@login_required
def scoreboard():


    #usr = current_user._get_current_object()
    
    users = User.query.order_by(User.score.desc()).all()

    return render_template('main/scoreboard.html', users = users)


@main.route('/help')
def help():


    return render_template('main/help.html')

@main.route('/close')
@login_required
@admin_required
def close_all_series():

    open_series = Series.query.filter(
        Series.open==True).all()



    return render_template('main/close_list.html',
        series = open_series)
