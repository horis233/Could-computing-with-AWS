from flask import Flask
from flask_bootstrap import Bootstrap
import os

# main = Blueprint(__name__)
webapp = Flask(__name__)
# webapp.secret_key = 'some_secret'
webapp.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()+'/uploads'
webapp.config['SECRET_KEY'] = 'hard to guess string'

Bootstrap(webapp)

from app import views
from app import forms
from app import thumbnails
