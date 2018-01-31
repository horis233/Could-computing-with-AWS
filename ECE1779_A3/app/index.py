import boto3
from flask import render_template, redirect, url_for, session
from app import webapp
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from boto3.dynamodb.conditions import Key
import os


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


@webapp.route('/<username>')
def index(username):
    # if 'username' in session:
    # if get_username() == username:
    #    if get_auth() is False:
    #        return redirect(url_for('frontpage'))
    if 'username' in session:
        if 'authenticated' not in session or session['username'] != username:
            return redirect(url_for('frontpage'))
        username_session = username
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        table = dynamodb.Table('Images')
        response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )

        urls = []
        if response is None:
            no_picture = True

        else:
            no_picture = False
            for image1 in response['Items']:
                url = s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': 'a3test2',
                        'Key': image1['image']
                    }
                )
                urls.append(url)

        return render_template('index.html', session_username=username_session, No_picture=no_picture
                               , urls=urls)
    return redirect(url_for('frontpage'))


@webapp.route('/<username>/<i>', methods=['GET'])
def thumb_view(username, i):
    if 'username' in session:
        if 'authenticated' not in session or session['username'] != username:
            return redirect(url_for('frontpage'))
        i = int(i)
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        table = dynamodb.Table('Images')
        response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        urls = []
        for image in response['Items']:
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': 'a3test2',
                    'Key': image['image']
                }
            )
            urls.append(url)
            background = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': 'a3test2',
                    'Key': 'background.png'
                }
            )
        return render_template('index_view.html', url=urls[i-1], username=username, i=i, background=background)
    return redirect(url_for('frontpage'))


@webapp.route('/<username>/delete_<i>')
def thumb_delete(username, i):
    if 'username' in session:
        if 'authenticated' not in session or session['username'] != username:
            return redirect(url_for('frontpage'))
        i = int(i)
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3_s = boto3.resource('s3',
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

        table = dynamodb.Table('Images')
        response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )

        image_i = 0
        for image in response['Items']:
            image_i = image_i + 1
            if image_i == i:
                bucket = s3_s.Bucket('a3test2')
                bucket.delete_objects(
                    Delete={
                        'Objects': [
                            {
                                'Key': image['image']
                            }
                        ]
                    }
                )
                table.delete_item(
                    Key={
                        'username': username,
                        'image': image['image']
                    },


                )
        response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
        urls = []
        for image in response['Items']:
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': 'a3test2',
                    'Key': image['image']
                }
            )
            urls.append(url)
        return redirect(url_for('index', username=username))
    return redirect(url_for('frontpage'))