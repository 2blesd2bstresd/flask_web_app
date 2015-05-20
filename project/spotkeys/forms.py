# project/users/forms.py

from flask_wtf import Form
from wtforms import TextField, DateField, IntegerField, \
                    SelectField, PasswordField, FloatField, BooleanField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Required, Length, EqualTo
from project.models import Spotkey
from project import db


class SpotkeyForm(Form):
    image = FileField('File Field')
    name = TextField('Task Name')
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')
    country = TextField('Country')
    zipcode = TextField('Zip Code')
    city = TextField('city')
    street = TextField('street')
    door_number = TextField('door_number')
    apartment_number = TextField('apartment_number')
    floor = TextField('floor')
    buzzer_code = TextField('buzzer_code')
    details = TextField('description')
    requires_navigation = BooleanField('disabled')
    state = TextField('state')
    cross_street = TextField('cross street')
    location_type = SelectField('Type', choices=[('home','Home'),
                                                 ('office','Office'),
                                                 ('business','Business'),
                                                 ('other','Other')])
    chain_id = SelectField('Choice')

class SpotForm(Form):
    image = FileField('File Field')
    spotkey_id = SelectField('Choice')#, choices=[(str(sk.id), sk.name) for sk in db.session.query(Spotkey).all()])
    latitude = TextField('Latitude')
    longitude = TextField('Longitude')
    details = TextField('description') 
    requires_navigation = BooleanField('disabled')
    transport_type = SelectField('Choice', choices=[('drive','Driving'), 
                                                    ('taxi','Taxi'), 
                                                    ('public','Public Tansportation'),
                                                    ('bike','Bike'),
                                                    ('walk','Walking')])
