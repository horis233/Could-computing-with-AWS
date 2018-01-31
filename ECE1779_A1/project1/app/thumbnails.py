from flask import Flask, request, render_template, redirect, url_for, flash, g
import mysql.connector
from config import db_config
import boto3
from app import webapp
from app.forms import connect_to_database, get_db

@webapp.route('/thumbnails/list/<username>', methods=['GET'])
def thumb_list(username):
    s3 = boto3.client('s3')
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''
               SELECT images.key1, images.key2, images.key3, images.key4 FROM images
               INNER JOIN users
               ON images.userId = users.id
               WHERE users.id = (SELECT id FROM users WHERE users.login = %s)
            '''
    cursor.execute(query, (username,))
    images=cursor.fetchall()
    # [('image1', 'r1image1', 'r2image1', 'r3image1'), ('image2', 'r1image2', 'r2image2', 'r3image2')]
    urls = []
    for image in images:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'ece1779project',
                'Key': image[0]
            }
        )
        urls.append(url)
    #print (urls)
    return render_template('/thumbnails/list.html', urls=urls, username=username)

@webapp.route('/thumbnails/view/<username>/<i>', methods=['GET'])
def thumb_view(username,i):
    i=int(i)
    s3 = boto3.client('s3')
    cnx = get_db()
    cursor = cnx.cursor()
    query = '''
                   SELECT images.key1, images.key2, images.key3, images.key4 FROM images
                   INNER JOIN users
                   ON images.userId = users.id
                   WHERE users.id = (SELECT id FROM users WHERE users.login = %s)
                '''
    cursor.execute(query, (username,))
    images = cursor.fetchall()
    urls = []
    for j in range(3):
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'ece1779project',
                'Key': images[i-1][j+1]
            }
        )
        urls.append(url)
    return render_template('/thumbnails/view.html', urls=urls)