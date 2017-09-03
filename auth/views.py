#!/usr/bin/python
# -*- coding: utf-8 -*-


from flask import render_template, redirect, request, url_for, flash, session
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm,RegisterForm, SetPassForm
from .. import db
from slugify import slugify



@auth.route('/login', methods=['GET', 'POST'])
def login():
    #session.pop('_flashes', None)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_name = form.username.data
        user = User.query.filter_by(username=user_name).first()

        if user is not None:
            flash('Već postoji korisnik {0}'.format(user_name))
            return redirect(url_for('main.index'))

        else:
            new_user = User(username=user_name,
                password=form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash(u'Dobrodošao {0}! Uloguj se.'.format(user_name))
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))




@auth.route('/setpass', methods=['GET', 'POST'])
@login_required
def setpass():
    if not current_user._get_current_object().is_admin:
        flash(u'Samo administrator!')
        return redirect(url_for('main.index'))

    form = SetPassForm()
    if form.validate_on_submit():
        user = form.username.data
        #user = User.query.filter_by(username=user_name).first()
        user.password = form.new_pass.data
            
        db.session.add(user)
        db.session.commit()

        flash(u'Izmenjen password za {0}!'.format(user.username))
        return redirect(url_for('main.index'))
    return render_template('auth/set_password.html', form=form)