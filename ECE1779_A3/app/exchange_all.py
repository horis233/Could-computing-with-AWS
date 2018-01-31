import random

from boto3.dynamodb.conditions import Key
from flask import render_template, redirect, url_for, request, session
from app import webapp
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import boto3
from app import swap, index

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))

s3 = boto3.resource('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3up = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
'''
class urlsvar:
    urls = None


def set_urls(urls):
    urlsvar.urls = urls


def get_urls():
    return urlsvar.urls
'''


@webapp.route('/exchange', methods=['GET'])
# Return file upload form
def exchange_all():

    if 'authenticated' not in session:
        return redirect(url_for('frontpage'))

    table = dynamodb.Table('s_image')
    response = table.query(
        KeyConditionExpression=Key('id').eq("1")
    )
    urls = []
    for s in response['Items']:
        url = s3up.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'a3test2',
                'Key': s['pic']
            }
        )
        urls.append(url)
    # set_urls(urls)
    session['urls'] = urls
    username = session['username']
    return render_template("upload/exchange.html", username=username, urls=urls)


@webapp.route('/image_exchange', methods=['POST'])
# Upload a new image and exchange it
def image_exchange():
    if 'authenticated' not in session:
        return redirect(url_for('frontpage'))
    username = session['username']
    # username = index.get_username()
    urls = session['urls']
    image1 = request.form.get('image1')
    if image1 == urls[0]:
        # s3.Bucket('a3test2').download_file('hc.jpg', 'app/static/hc.jpg')
        f1 = 'app/static/bigxi.jpg'
    if image1 == urls[1]:
        # s3.Bucket('a3test2').download_file('hu.jpg', 'app/static/hu.jpg')
        f1 = 'app/static/emilia.jpg'
    if image1 == urls[2]:
        # s3.Bucket('a3test2').download_file('kobe.jpg', 'app/static/kobe.jpg')
        f1 = 'app/static/emma.jpg'
    if image1 == urls[3]:
        # s3.Bucket('a3test2').download_file('kobe.jpg', 'app/static/kobe.jpg')
        f1 = 'app/static/hc.jpg'
    if image1 == urls[4]:
        f1 = 'app/static/hu.jpg'
    if image1 == urls[5]:
        f1 = 'app/static/justin.jpg'
    if image1 == urls[6]:
        f1 = 'app/static/kobe.jpg'
    if image1 == urls[7]:
        f1 = 'app/static/na.jpg'
    if image1 == urls[8]:
        f1 = 'app/static/pu.jpg'
    if image1 == urls[9]:
        f1 = 'app/static/taylor.jpg'

    image2 = request.form.get('image2')
    if image2 == urls[0]:
        # s3.Bucket('a3test2').download_file('hc.jpg', 'app/static/hc.jpg')
        f2 = 'app/static/bigxi.jpg'
    if image2 == urls[1]:
        # s3.Bucket('a3test2').download_file('hu.jpg', 'app/static/hu.jpg')
        f2 = 'app/static/emilia.jpg'
    if image2 == urls[2]:
        # s3.Bucket('a3test2').download_file('kobe.jpg', 'app/static/kobe.jpg')
        f2 = 'app/static/emma.jpg'
    if image2 == urls[3]:
        # s3.Bucket('a3test2').download_file('kobe.jpg', 'app/static/kobe.jpg')
        f2 = 'app/static/hc.jpg'
    if image2 == urls[4]:
        f2 = 'app/static/hu.jpg'
    if image2 == urls[5]:
        f2 = 'app/static/justin.jpg'
    if image2 == urls[6]:
        f2 = 'app/static/kobe.jpg'
    if image2 == urls[7]:
        f2 = 'app/static/na.jpg'
    if image2 == urls[8]:
        f2 = 'app/static/pu.jpg'
    if image2 == urls[9]:
        f2 = 'app/static/taylor.jpg'

    # save the picture into dictionory and bucket
    OVERLAY_POINTS = [
        LEFT_EYE_POINTS + RIGHT_EYE_POINTS + LEFT_BROW_POINTS + RIGHT_BROW_POINTS,
        NOSE_POINTS + MOUTH_POINTS,
    ]

    #swap.set_error(None)
    session['error_msg'] = None

    part = "all"

    swap.main(image1=f1, image2=f2,  username=username, OVERLAY_POINTS=OVERLAY_POINTS, part=part)

    return redirect(url_for('index', username=username))

