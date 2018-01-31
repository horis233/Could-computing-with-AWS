from boto3 import dynamodb
from boto3.dynamodb.conditions import Key
from flask import render_template, session, request, redirect, url_for
from app import webapp, index
from hashlib import md5
import boto3

webapp.secret_key = 'Pb?\x80\xe2R>\x14\x1fk\x0b\x9fV\x0b\xf2\xe2\x1a$\xc9\xf2`\x11d\xd6'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


class Error(Exception): pass


@webapp.route('/login_submit',methods=['GET','POST'])
def login():
    error_msg = None
    username = None

    #if index.get_username() is not None and index.get_auth() is True:
     #   username = index.get_username()
      #  return redirect(url_for('index', username=username))
    if 'username' in session and session['authenticated'] is True:
        username = session['username']
        return redirect(url_for('index', username=username))

    elif request.method == 'GET':
        return render_template('login.html')

    try:
        if request.method == 'POST':

            username = request.form['userID']
            table = dynamodb.Table('Users')
            response = table.query(
                KeyConditionExpression=Key('username').eq(username)
            )
            if response['Count'] == 0:
                raise Error('Invalid name')

            o_password = request.form['password']
            password = md5()
            password.update(bytes(o_password))

            for row in response['Items']:
                if password.hexdigest() == row['password']:

                    #index.set_username(request.form['userID'])
                    #index.set_auth(True)
                    session['username'] = request.form['userID']
                    session['authenticated'] = True
                    return redirect(url_for('index', username=username))
            raise Error('password error')
    except Error as error_catch:
        error_msg = str(error_catch)

    return render_template('login.html', error_msg=error_msg, username=username)


@webapp.route('/logout',methods=['GET','POST'])
def logout():
    #index.set_auth(False)
    #index.set_username(None)
    session.clear()
    return redirect(url_for('frontpage'))

#def encrypt_password():
