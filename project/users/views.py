# project/users/views.py


#################
#### imports ####
#################
import threading
from functools import wraps
from flask import flash, redirect, render_template, \
    request, session, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
import boto
from boto.s3.key import Key
from .forms import RegisterForm, LoginForm
from project import db, bcrypt, config
from project.models import User, Contact
from uuid import uuid4


################
#### config ####
################

users_blueprint = Blueprint('users', __name__)


##########################
#### helper functions ####
##########################
def add_contact(new_user, contact):

    print 'THREAD START: ', contact.id
    # Add existing user as contacts for new user
    new_contact = Contact(new_user.id, contact.id, contact.username, contact.profile_url)
    db.session.add(new_contact)
    db.session.commit()

    # Add new user as contact for existing user
    new_contact = Contact(contact.id, new_user.id, new_user.username, new_user.profile_url)
    db.session.add(new_contact)
    db.session.commit()

    print 'THREAD END: ', contact.id


def s3_upload(source_file):

    conn = boto.connect_s3(config.KEY, config.SECRET)
    b = conn.get_bucket(config.BUCKET)

    k = Key(b)
    k.key = str(uuid4())

    k.set_contents_from_file(source_file)
    # k.set_contents_from_string(source_file.data)
    
    return 'https://s3-us-west-1.amazonaws.com/spotkey-host/' + k.key


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('users.login'))
    return wrap


################
#### routes ####
################

@users_blueprint.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Goodbye!')
    return redirect(url_for('users.login'))


@users_blueprint.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=request.form['username']).first()
            if user is not None and bcrypt.check_password_hash(
                    user.password, request.form['password']):
                session['logged_in'] = True
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Welcome!')
                return redirect(url_for('spotkeys.spotkeys'))
            else:
                error = 'Invalid username or password.'
    return render_template('login.html', form=form, error=error)


@users_blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():

            output = s3_upload(request.files['image'])

            new_user = User(
                form.username.data,
                bcrypt.generate_password_hash(form.password.data),
                email=form.email.data,
                profile_url = output
            )
            try:
                db.session.add(new_user)
                db.session.commit()

                # Asynchronously add contact info
                users = User.query.filter(User.id!=new_user.id).all()                
                for u in users:
                    threading.Thread(target=add_contact(new_user, u))

                flash('Thanks for registering. Please login.')
                return redirect(url_for('users.login'))
            except IntegrityError:
                error = 'That username and/or email already exist.'
                return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)
