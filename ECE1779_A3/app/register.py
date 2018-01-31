from boto3 import dynamodb
from boto3.dynamodb.conditions import Key
from flask import render_template,request,redirect,url_for
from app import webapp
from hashlib import md5
import boto3
webapp.secret_key = 'Pb?\x80\xe2R>\x14\x1fk\x0b\x9fV\x0b\xf2\xe2\x1a$\xc9\xf2`\x11d\xd6'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

@webapp.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':

        # get username and password
        u = request.form.get('username', "")
        o_p = request.form.get('password', "")
        error = False

        # judge the inputs are empty
        if u == "" or o_p == "":
            error = True
            error_msg = "Error: All fields are required!"

        # add salt to password
        p = md5()
        p.update(bytes(o_p))

        # check the username in db
        table = dynamodb.Table('Users')
        response = table.query(
            KeyConditionExpression=Key('username').eq(u)
        )

        if response['Count'] != 0:
            error = True
            error_msg = "Error: This username has existed"

        # if error return to register.html
        if error:
            return render_template("register.html", title="Error", error_msg=error_msg, username=u)

        # write username and password into db
        table.put_item(
            Item={
                'username': u,
                'password': p.hexdigest(),
            }
        )

        return redirect(url_for('frontpage'))
