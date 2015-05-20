# project/tasks/views.py
import datetime
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, \
                  session, url_for, g, Blueprint

from functools import wraps
from .forms import SpotForm, SpotkeyForm
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import exc, asc, desc, or_
from project import db
from project.models import User, Spotkey, Spot
from project import config
from uuid import uuid4
import boto
from boto.s3.key import Key
import os.path
# from flask import current_app as app
from werkzeug import secure_filename


app = db.app


################
#### config ####
################

spotkeys_blueprint = Blueprint('spotkeys', __name__)


##########################
#### helper functions ####
##########################

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('users.login'))
    return wrap


def s3_upload(source_file):

    conn = boto.connect_s3(config.KEY, config.SECRET)
    b = conn.get_bucket(config.BUCKET)

    k = Key(b)
    k.key = str(uuid4())

    k.set_contents_from_file(source_file)
    # k.set_contents_from_string(source_file.data)
    
    return 'https://s3-us-west-1.amazonaws.com/spotkey-host/' + k.key

def active_spotkeys():
    result = []
    sks = db.session.query(Spotkey).filter_by(
        share_with_all=True).filter_by(owner_id=session['user_id'])
    for sk in sks:
        result.append({'spotkey': sk, 'spot_count': db.session.query(Spot).filter_by(spotkey_id=sk.id).count()})
    return result

def inactive_spotkeys():
    result = []
    sks = db.session.query(Spotkey).filter_by(
        share_with_all=False).filter_by(owner_id=session['user_id'])
    for sk in sks:

        result.append({'spotkey': sk, \
                       'spots': db.session.query(Spot).filter_by(spotkey_id=sk.id).all(), \
                       'spot_count': db.session.query(Spot).filter_by(spotkey_id=sk.id).count()})
    return result


################
#### routes ####
################

@spotkeys_blueprint.route('/spotkeys/')
@login_required
def spotkeys():
    """
    Get user's spotkeys and fill choices for spotkey dropdown on spot form.
    """

    spotkey_ids = []

    for sk in Spotkey.query.filter_by(owner_id=session['user_id']).order_by(Spotkey.id).all():
        spotkey_ids.append((str(sk.id), sk.name))

    spot_form = SpotForm()
    spot_form.spotkey_id.choices = spotkey_ids

    chain_ids = spotkey_ids[:]
    chain_ids.insert(0, ('', 'None'))
    spotkey_form = SpotkeyForm(request.form)
    spotkey_form.chain_id.choices = chain_ids

    return render_template(
        'spotkeys.html',
        spotkey_form=spotkey_form,
        active_spotkeys=active_spotkeys(),
        inactive_spotkeys=inactive_spotkeys(),
        spot_form=spot_form,
        username=session['username']
            )


@spotkeys_blueprint.route('/create_spotkey/', methods=['GET', 'POST'])
@login_required
def create_spotkey():

    spotkey_ids = [('', 'None')]

    for sk in Spotkey.query.filter_by(owner_id=session['user_id']).order_by(Spotkey.id).all():
        spotkey_ids.append((str(sk.id), sk.name))

    form = SpotkeyForm(request.form)

    form.chain_id.choices = spotkey_ids
    error = []

    if request.method == 'POST':

        if form.validate_on_submit():

            output = s3_upload(request.files['image'])
            
            u = User.query.filter_by(id=session['user_id']).first()

            # Add a chain id
            chain_id = form.data['chain_id'] if form.data['chain_id'] else None

            if chain_id:
                sp = Spotkey.query.filter_by(id=chain_id)

            sk = Spotkey(session['user_id'], 
                         form.name.data, 
                         datetime.now(), 
                         location_type=form.location_type.data,
                         profile_url=u.profile_url,
                         chain_id=chain_id,
                         nav_types='all')

            db.session.add(sk)
            db.session.commit()
            
            s = Spot(sk.id, 1, picture_url=output, transport_type='all',
                     latitude=form.latitude.data, longitude=form.longitude.data,
                     details=form.details.data, requires_navigation=False)

            db.session.add(s)
            db.session.commit()

            sk.primary_spot_id = s.id
            db.session.add(sk)
            db.session.commit()

            flash('New entry was successfully posted. Thanks.')
            return redirect(url_for('spotkeys.spotkeys'))

    flash('Invalid data.')
    return redirect(url_for('spotkeys.spotkeys'))


@spotkeys_blueprint.route('/add_spot/', methods=['GET', 'POST'])
@login_required
def add_spot():

    spotkey_ids = []

    for sk in Spotkey.query.filter_by(owner_id=session['user_id']).order_by(Spotkey.id).all():
        spotkey_ids.append((str(sk.id), sk.name))

    form = SpotForm(request.form)
    form.spotkey_id.choices = spotkey_ids

    error = []
    if request.method == 'POST':

        if form.validate_on_submit():

            output = s3_upload(request.files['image'])

            # decrement priority
            # find spot with highest priority
            priority_spot = db.session.query(Spot).filter(Spot.spotkey_id==form.spotkey_id.data) \
                                                  .filter(Spot.priority > 1) \
                                                  .order_by(asc(Spot.priority)) \
                                                  .first()

            # set first
            if not priority_spot:
                priority=100
            else:
                priority = priority_spot.priority - 1

            latitude = form.latitude.data if form.latitude.data else 0.0
            longitude = form.longitude.data if form.longitude.data else 0.0

            s = Spot(spotkey_id=form.spotkey_id.data, 
                     priority=priority, 
                     picture_url=output,
                     latitude=latitude, 
                     longitude=longitude,
                     requires_navigation=form.requires_navigation.data,
                     details=form.details.data,
                     transport_type=form.transport_type.data)
            db.session.add(s)
            db.session.commit()

            flash('New dartkey was successfully pinned. Thanks.')
            return redirect(url_for('spotkeys.spotkeys'))
    return redirect(url_for('spotkeys.spotkeys'))
    # return render_template(
    #     'spotkeys.html',
    #     spot_form=form,
    #     error=error,
    #     active_spotkeys=active_spotkeys(),
    #     inactive_spotkeys=inactive_spotkeys()
    # )


@spotkeys_blueprint.route('/activate/<int:spotkey_id>/')
@login_required
def activate(spotkey_id):
    db.session.query(Spotkey).filter_by(id=spotkey_id).update({'share_with_all': True})
    db.session.commit()
    flash ("SpotKey activated.")
    return redirect(url_for('spotkeys.spotkeys'))


@spotkeys_blueprint.route('/deactivate/<int:spotkey_id>') 
@login_required
def deactivate(spotkey_id):
    db.session.query(Spotkey).filter_by(id=spotkey_id).update({'share_with_all': False})
    db.session.commit()
    flash('SpotKey deactivated.')
    return redirect(url_for('spotkeys.spotkeys'))


@spotkeys_blueprint.route('/delete/<int:spotkey_id>')
@login_required
def delete(spotkey_id):
    sk = db.session.query(Spotkey).filter_by(id=spotkey_id).update({'primary_spot_id':None})
    db.session.commit()
    db.session.query(Spot).filter_by(spotkey_id=spotkey_id).delete()
    db.session.commit()
    db.session.query(Spotkey).filter_by(id=spotkey_id).delete()
    db.session.commit()
    flash ("SpotKey deleted.")
    return redirect(url_for('spotkeys.spotkeys'))


@spotkeys_blueprint.route('/delete_spot/<int:spot_id>')
@login_required
def delete_spot(spot_id):
    db.session.query(Spot).filter_by(id=spot_id).delete()
    db.session.commit()
    flash ("Spot deleted.")
    return redirect(url_for('spotkeys.spotkeys'))

