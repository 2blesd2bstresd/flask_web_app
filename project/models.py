import uuid
import datetime
from database import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    profile_url = db.Column(db.String)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    tether_id = db.Column(db.String)
    user_type = db.Column(db.String)
    create_date = db.Column(db.DateTime(), default=db.func.now())

    def __init__(self, username, password, first_name=None, 
                 last_name=None, email=None, profile_url=None, 
                 create_date=None, tether_id=None, user_type='personal'):

        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.profile_url = profile_url
        self.create_date = create_date
        self.tether_id = tether_id
        self.user_type = user_type

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.username)


class Spotkey(db.Model):

    __tablename__ = "spotkeys"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer)
    location_type = db.Column(db.String)
    primary_spot_id = db.Column(db.Integer)
    name = db.Column(db.String)
    create_date = db.Column(db.DateTime(), default=db.func.now())
    share_with_all = db.Column(db.Boolean)
    profile_url = db.Column(db.String)
    nav_types = db.Column(db.String)
    chain_id = db.Column(db.String)

    def __init__(self, owner_id, name, create_date=None, 
                 location_type=None, share_with_all=False, 
                 primary_spot_id=None, profile_url=None,
                 nav_types=None, chain_id=None): 

        self.owner_id = owner_id
        self.name = name
        self.create_date = create_date
        self.primary_spot_id = primary_spot_id
        self.location_type = location_type
        self.share_with_all = share_with_all
        self.profile_url = profile_url
        self.nav_types = nav_types
        self.chain_id = chain_id

    def __repr__(self):
        return '<Spotkey %r>' % self.name

    def primary_spot(self):
        return db.session.query(Spot).filter_by(id=self.primary_spot_id).first()


class Spot(db.Model):

    __tablename__ = "spots"

    id = db.Column(db.Integer, primary_key=True)
    spotkey_id = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, nullable=False) 
    street_address = db.Column(db.String)
    street_address_2 = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zipcode = db.Column(db.String)
    transport_type = db.Column(db.String)
    buzzer_code = db.Column(db.String)
    requires_navigation = db.Column(db.Boolean)
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)
    door_number = db.Column(db.Integer)
    details = db.Column(db.String)
    cross_street = db.Column(db.String)
    picture_url = db.Column(db.String)
    create_date = db.Column(db.DateTime(), default=db.func.now())


    def __init__(self, spotkey_id, priority, transport_type='Any', requires_navigation=False, 
                 latitude=None, longitude=None, street_address=None, street_address_2=None, 
                 city=None, state=None, zipcode=None, buzzer_code=None, door_number=None, 
                 details=None, cross_street=None, picture_url=None, create_date=None):

        self.spotkey_id = spotkey_id
        self.priority = priority
        self.transport_type = transport_type
        self.requires_navigation = requires_navigation
        self.latitude = latitude
        self.longitude = longitude
        self.street_address = street_address
        self.street_address_2 = street_address_2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.buzzer_code = buzzer_code
        self.door_number = door_number
        self.details = details
        self.cross_street = cross_street
        self.picture_url = picture_url
        self.create_date = create_date

    def __repr__(self):
        return '<Spot %r>' % self.priority


class Contact(db.Model):

    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    primary_id = db.Column(db.Integer, nullable=False)
    contact_id = db.Column(db.Integer, nullable=False) 
    contact_username = db.Column(db.String)
    profile_url = db.Column(db.String)
    create_date = db.Column(db.DateTime(), default=db.func.now())


    def __init__(self, primary_id, contact_id, contact_username, profile_url=None):

        self.primary_id = primary_id
        self.contact_id = contact_id
        self.contact_username = contact_username
        self.profile_url = profile_url

    def __repr__(self):
        return '<Contact>'


class View(db.Model):

    __tablename__ = "views"

    id = db.Column(db.String, default=lambda:str(uuid.uuid4()), primary_key = True)
    user_id = db.Column(db.Integer, nullable=False)
    spotkey_id = db.Column(db.Integer, nullable=False)
    create_date = db.Column(db.DateTime(), default=db.func.now())

    def __init__(self, user_id, spotkey_id):

        self.user_id = user_id
        self.spotkey_id = spotkey_id

    def __repr__(self):
        return '<View>'

class Session(db.Model):

    __tablename__ = "sessions"

    id = db.Column(db.String(40), default=lambda:str(uuid.uuid4()), primary_key = True)
    user_id = db.Column(db.Integer, nullable=False)
    create_date = db.Column(db.DateTime(), default=db.func.now())
    modified_date = db.Column(db.DateTime(), default=db.func.now())

    def __init__(self, user_id):

        self.user_id = user_id

    def __repr__(self):
        return '<Session %r>' % user_id
