from flask import Flask, request, render_template, redirect, url_for, flash, g
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

import mysql.connector
from config import db_config

import tempfile
import os
import boto3

from app import webapp
from wand.image import Image

photos = UploadSet('photos', IMAGES)
configure_uploads(webapp, photos)
patch_request_class(webapp)

'''

Class Definitions

'''

class RegisterForm(FlaskForm):
    username = StringField(u'Username', validators=[
                DataRequired(message= u'Username can not be empty.'), Length(4, 16)])
    password = PasswordField('New Password', validators=[
        DataRequired(message= u'Password can not be empty.'),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField(u'Register')

class LoginForm(FlaskForm):
    username = StringField(u'Username', validators=[
               DataRequired(message=u'Username can not be empty.'), Length(4, 16)])
    password = PasswordField(u'Password',
                             validators=[DataRequired(message=u'Password can not be empty.')])
    submit = SubmitField(u'Login')

'''

Functions for Database

'''

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
# this will execute every time when the context is closed
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

'''

Routers for Login

'''

@webapp.route('/login', methods=['GET', 'POST'])
# Display an empty HTML form that allows users to login
# check the database for existing username and password
# if not right, return to this page again
def login():
    form = LoginForm()
    username = request.form.get('username')
    password = request.form.get('password')
    if form.validate_on_submit():
        cnx = get_db()
        cursor=cnx.cursor()
        query = '''SELECT * FROM users WHERE login = %s
        '''
        cursor.execute(query,(username,))
        if cursor.fetchone() is None:
            flash(u"Username doesn't exist!",'warning')
            return render_template("/login/login.html",form=form)
        else:
            query = '''SELECT * FROM users WHERE login = %s AND password = %s
            '''
            cursor.execute(query,(username,password))
            if cursor.fetchone() is None:
                flash(u"Password is wrong!",'warning')
                return  render_template("/login/login.html",form=form)
            else:
                flash(u"Login Success!",'success')
                return redirect(url_for('thumb_list', username=username))
    return render_template("/login/login.html", form=form)

'''

Routers for Register

'''
@webapp.route('/register', methods=['GET', 'POST'])
# Display an empty HTML form that allows users to register a new account
# If everything in the form are right, save them in the dataabse to create a new account for the new user
def register():
    form = RegisterForm()
    username = request.form.get('username')
    password = request.form.get('password')
    if form.validate_on_submit():
        cnx = get_db()
        cursor = cnx.cursor()
        query = '''SELECT * FROM users WHERE login = %s'''
        cursor.execute(query, (username,))
        if cursor.fetchone() is not None:
            flash(u"That username is already taken.",'warning')
            return render_template("/register/register.html", form=form)
        else:
            query = ''' INSERT INTO users (login, password)
                               VALUES (%s,%s)
            '''
            cursor.execute(query, (username, password))
            cnx.commit()
            flash(u"Register Success!",'success')
            return render_template("/fileupload/form.html")
    return render_template("/register/register.html", form=form)

'''

Routers for Uploading Images

'''

@webapp.route('/FileUpload/form',methods=['GET'])
#Return file upload form
def upload_form():
    return render_template("/fileupload/form.html")

@webapp.route('/FileUpload', methods=['GET','POST'])
#Show the uploaded image
def upload_file():
    if request.method == 'POST':
        userid = request.form.get("userID")
        password = request.form.get("password")

        # check if the post request has the file part
        if 'uploadedfile' not in request.files:
            # return "Missing uploaded file"
            flash(u'Missing uploaded file', 'warning')
            return render_template("/fileupload/form.html")

        file = request.files['uploadedfile']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # return 'Missing file name'
            flash(u"Missing file name", 'warning')
            return render_template("/fileupload/form.html")

        if file:
            # query the database to find whether the account exist and the password is right
            cnx = get_db()
            cursor = cnx.cursor()
            query = '''SELECT * FROM users WHERE login = %s AND password = %s
            '''
            cursor.execute(query,(userid,password))
            row = cursor.fetchone()
            if row is not None:
                s3 = boto3.client('s3')

                # save the uploaded file into uploads directory and S3 bucket
                filename = photos.save(request.files['uploadedfile'])
                file_url = photos.url(filename)

                # rotate the image and save the 3 transformed image files into uploads directory and s3 bucket
                fname = os.path.join('uploads', file.filename)
                img = Image(filename=fname)
                with open(fname, "rb") as image0:
                    s3.upload_fileobj(image0, 'ece1779project', file.filename)
                i = img.clone()
                i.rotate(90)
                fname_rotated1 = os.path.join('uploads','rotated1_'+ file.filename)
                i.save(filename=fname_rotated1)
                with open(fname_rotated1, "rb") as image1:
                    s3.upload_fileobj(image1, 'ece1779project', 'rotated1_'+ file.filename)

                i.rotate(90)
                fname_rotated2 = os.path.join('uploads', 'rotated2_' + file.filename)
                i.save(filename=fname_rotated2)
                with open(fname_rotated2, "rb") as image2:
                    s3.upload_fileobj(image2, 'ece1779project', 'rotated2_'+ file.filename)

                i.rotate(90)
                fname_rotated3 = os.path.join('uploads', 'rotated3_' + file.filename)
                i.save(filename=fname_rotated3)
                with open(fname_rotated3, "rb") as image3:
                    s3.upload_fileobj(image3, 'ece1779project', 'rotated3_'+ file.filename)

                query = '''INSERT INTO images (userid, key1, key2, key3, key4)
                               VALUES (%s,%s,%s,%s,%s)
                '''
                cursor.execute(query,(int(row[0]),file.filename,'rotated1_'+ file.filename,'rotated2_' + file.filename,'rotated3_' + file.filename))
                cnx.commit()
                flash(u"Upload Success!", 'success')
                return render_template("base.html") + '<br><img src=' + file_url + '>'
            else:
                flash(u"Username does not exist or password is wrong!",'warning')
                return render_template("/fileupload/form.html")
    return render_template("base.html")

'''

Routers for Transforming Images

'''

@webapp.route('/imagetransform/form',methods=['GET'])
#Return file upload form
def image_form():
    return render_template("/imagetransform/form.html")

@webapp.route('/imagetransform',methods=['POST'])
#Upload a new image and tranform it
def image_transform():

    # check if the post request has the file part
    if 'image_file' not in request.files:
        return "Missing uploaded file"

    new_file = request.files['image_file']

    # if user does not select file, browser also
    # submit a empty part without filename
    if new_file.filename == '':
        return "Missing file name"

    tempdir = tempfile.gettempdir()

    fname = os.path.join('app/static',new_file.filename)


    new_file.save(fname)
    #print (fname)
    img = Image(filename=fname)
    i = img.clone()
    i.rotate(90)

    fname_rotated = os.path.join('app/static', 'rotated_' + new_file.filename)

    i.save(filename=fname_rotated)

    return render_template("/imagetransform/view.html",
                           f1=fname[4:],
                           f2=fname_rotated[4:])


'''

Test Functions

'''
@webapp.route('/test/FileUpload',methods=['GET','POST'])
#Upload a new file and store in the systems temp directory
def file_upload_test():
    if request.method == 'POST':
        userid = request.form.get("userID")
        password = request.form.get("password")

        # check if the post request has the file part
        if 'uploadedfile' not in request.files:
            return "Missing uploaded file"

        file = request.files['uploadedfile']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return 'Missing file name'

        if file:
            # query the database to find whether the account exist and the password is right
            cnx = get_db()
            cursor = cnx.cursor()
            query = '''SELECT * FROM users WHERE login = %s AND password = %s
            '''
            cursor.execute(query, (userid, password))
            row = cursor.fetchone()
            if row is not None:
                s3 = boto3.client('s3')

                # save the uploaded file into uploads directory and S3 bucket
                filename = photos.save(request.files['uploadedfile'])
                file_url = photos.url(filename)

                # rotate the image and save the 3 transformed image files into uploads directory and s3 bucket
                fname = os.path.join('uploads', file.filename)
                img = Image(filename=fname)
                with open(fname, "rb") as image0:
                    s3.upload_fileobj(image0, 'ece1779project', file.filename)
                i = img.clone()
                i.rotate(90)
                fname_rotated1 = os.path.join('uploads', 'rotated1_' + file.filename)
                i.save(filename=fname_rotated1)
                with open(fname_rotated1, "rb") as image1:
                    s3.upload_fileobj(image1, 'ece1779project', 'rotated1_' + file.filename)

                i.rotate(90)
                fname_rotated2 = os.path.join('uploads', 'rotated2_' + file.filename)
                i.save(filename=fname_rotated2)
                with open(fname_rotated2, "rb") as image2:
                    s3.upload_fileobj(image2, 'ece1779project', 'rotated2_' + file.filename)

                i.rotate(90)
                fname_rotated3 = os.path.join('uploads', 'rotated3_' + file.filename)
                i.save(filename=fname_rotated3)
                with open(fname_rotated3, "rb") as image3:
                    s3.upload_fileobj(image3, 'ece1779project', 'rotated3_' + file.filename)

                query = '''INSERT INTO images (userid, key1, key2, key3, key4)
                               VALUES (%s,%s,%s,%s,%s)
                '''
                cursor.execute(query, (int(row[0]), file.filename, 'rotated1_' + file.filename, 'rotated2_' + file.filename,
                                       'rotated3_' + file.filename))
                cnx.commit()
                return "Success"
    else:
        return render_template("/fileupload/test.html")