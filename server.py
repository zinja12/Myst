from flask import Flask, g, render_template, flash, redirect, url_for
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user

import dropbox
from dropbox import *

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'the secret history in the dragonbone catacombs'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

dbx = dropbox.Dropbox('xy5UX6Om8VsAAAAAAAA2mM2pFrL6VXtghC8zJP-Q_3STbJ_QJfJduAX-y6kB5ezl')
dbx.users_get_current_account()

@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request"""
    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Registration successful.", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password is invalid", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login success", "success")
                return redirect(url_for('usr_home'))
            else:
                flash("Your email or password is invalid", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout success", "success")
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/usr_home')
@login_required
def usr_home():
    return render_template('usr_home.html', dbx=dbx)

@app.route('/usr_settings', methods=('GET', 'POST'))
@login_required
def usr_settings():
    form1 = forms.DropboxForm()
    form2 = forms.GoogleDriveForm()
    if form1.validate_on_submit() and form2.validate_on_submit():
        flash("Dropbox stuff happens with magic!", "success")
    return render_template('usr_settings.html', form1=form1, form2=form2)

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='shaan',
            email='x3zinja12@gmail.com',
            password='admin',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG)
