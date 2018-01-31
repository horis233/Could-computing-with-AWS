from flask import render_template, redirect, url_for, request, session
from app import webapp
from boto3.dynamodb.conditions import Key
import os
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import boto3
from app import swap

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))

'''
class urlsvar:
    urls = None


def set_urls(urls):
    urlsvar.urls = urls


def get_urls():
    return urlsvar.urls


class picvar:
    pic = None


def set_pic(pic):
    picvar.pic = pic


def get_pic():
    return picvar.pic
'''


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

s3 = boto3.resource('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

s3up = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


class Error(Exception): pass


@webapp.route('/exchange_part', methods=['GET'])
# Return file upload form
def exchange_part():
    #if index.get_auth() is False:
     #   return redirect(url_for('frontpage'))
    if 'authenticated' not in session:
        return redirect(url_for('frontpage'))
    username = session['username']
    #username = index.get_username()
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
    session['urls'] = urls
    # set_urls(urls)
    # print('1')
    # print(urls)
    return render_template("upload/expart.html", username=username, urls=urls)


@webapp.route('/image_exchange_part', methods=['POST'])
# Upload a new image and exchange it
def image_exchange_part():
    if 'authenticated' not in session:
        return redirect(url_for('frontpage'))
    username = session['username']
    # username = index.get_username()

    urls = session['urls']
    # urls = get_urls()
    # print('2')
    # print(urls)
    image3 = request.form.get('image3')
    if image3 == urls[0]:
        # s3.Bucket('a3test2').download_file('hc.jpg', 'app/static/hc.jpg')
        f3 = 'app/static/bigxi.jpg'
    if image3 == urls[1]:
        # s3.Bucket('a3test2').download_file('hu.jpg', 'app/static/hu.jpg')
        f3 = 'app/static/emilia.jpg'
    if image3 == urls[2]:
        # s3.Bucket('a3test2').download_file('kobe.jpg', 'app/static/kobe.jpg')
        f3 = 'app/static/emma.jpg'
    if image3 == urls[3]:
        # s3.Bucket('a3test2').download_file('kobe.jpg', 'app/static/kobe.jpg')
        f3 = 'app/static/hc.jpg'
    if image3 == urls[4]:
        f3 = 'app/static/hu.jpg'
    if image3 == urls[5]:
        f3 = 'app/static/justin.jpg'
    if image3 == urls[6]:
        f3 = 'app/static/kobe.jpg'
    if image3 == urls[7]:
        f3 = 'app/static/na.jpg'
    if image3 == urls[8]:
        f3 = 'app/static/pu.jpg'
    if image3 == urls[9]:
        f3 = 'app/static/taylor.jpg'

    try:

        # check if the post request has the file part
        if 'image_file' not in request.files:
            raise Error('Missing uploaded file')

        new_file = request.files['image_file']

        if new_file.filename == '':
            raise Error('Missing file name')

        if not allowed_file(new_file.filename):
            raise Error('File type not supported')
    except Error as error_catch:
        error_msg = str(error_catch)
        return render_template("upload/expart.html", username=username, error_msg=error_msg, urls=urls)

    fname = os.path.join('/tmp/', new_file.filename)
    new_file.save(fname)

    with open(fname, "rb") as image0:
        s3up.upload_fileobj(image0, 'a3test2', new_file.filename)

    # save the picture into dictionory and bucket

    part = request.form.get('part')

    if part == 'eyes':
        OVERLAY_POINTS = [LEFT_EYE_POINTS + RIGHT_EYE_POINTS, ]
        partname = "eyes"
    if part == 'brow':
        OVERLAY_POINTS = [LEFT_BROW_POINTS + RIGHT_BROW_POINTS, ]
        partname = "brow"
    if part == 'nose':
        OVERLAY_POINTS = [NOSE_POINTS, ]
        partname = "nose"
    if part == 'mouse':
        OVERLAY_POINTS = [MOUTH_POINTS, ]
        partname = "mouse"

    idpic = str(username + fname[11:-4] + f3[11:-4] + partname)
    session['pic'] = '/tmp/' + idpic + '.jpg'
    # set_pic('/tmp/' + idpic + '.jpg')
    swap.main(image1=fname, image2=f3, username=username, OVERLAY_POINTS=OVERLAY_POINTS, part=partname)
    '''
    print(swap.get_error())
    if swap.get_error() is None:
        #print("comes here!")
        return redirect(url_for('exchange_part_process'))

    error_msg = swap.get_error()
    swap.set_error(None)
    '''
    if session['error_msg'] is None:
        #print("comes here!")
        return redirect(url_for('exchange_part_process'))

    error_msg = session['error_msg']
    session['error_msg'] = None
    return render_template("upload/expart.html", username=username, error_msg=error_msg, urls=urls)
