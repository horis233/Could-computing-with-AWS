from flask import render_template, redirect, url_for, request, session
from app import webapp
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import boto3
from app import swap, exchange_part, index

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.resource('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3up = boto3.client('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))




@webapp.route('/exchange_part_process')
# Return file upload form
def exchange_part_process():
    #if index.get_auth() is False:
    #    return redirect(url_for('frontpage'))
    if 'authenticated' not in session:
        return redirect(url_for('frontpage'))
    username = session['username']
    #username = index.get_username()
    # urls = exchange_part.get_urls()
    # exchange_part.set_urls(urls)
    # print(exchange_part.get_urls())
    urls = session['urls']
    url = session['url']
    #print(url)
    return render_template("upload/expart_process.html", username=username, url=url, urls=urls)


@webapp.route('/image_exchange_part_process', methods=['POST'])
# Upload a new image and exchange it
def image_exchange_part_process():

    if 'authenticated' not in session:
        return redirect(url_for('frontpage'))
    username = session['username']
    # username = index.get_username()

    # pic = exchange_part.get_pic()
    urls = session['urls']
    #urls = exchange_part.get_urls()
    #urls = geturls()
    #print(urls)
    image4 = request.form.get('image4')
    if image4 == urls[0]:
        #s3.Bucket('a3test2').download_file('hc.jpg', 'app/static/hc.jpg')
        f4 = 'app/static/bigxi.jpg'
    if image4 == urls[1]:
        #s3.Bucket('a3test2').download_file('hu.jpg', 'app/static/hu.jpg')
        f4 = 'app/static/emilia.jpg'
    if image4 == urls[2]:
        #s3.Bucket('a3test2').download_file('kobe.jpg', 'app/static/kobe.jpg')
        f4 = 'app/static/emma.jpg'
    if image4 == urls[3]:
        # s3.Bucket('a3test2').download_file('kobe.jpg', 'app/static/kobe.jpg')
        f4 = 'app/static/hc.jpg'
    if image4 == urls[4]:
        f4 = 'app/static/hu.jpg'
    if image4 == urls[5]:
        f4 = 'app/static/justin.jpg'
    if image4 == urls[6]:
        f4 = 'app/static/kobe.jpg'
    if image4 == urls[7]:
        f4 = 'app/static/na.jpg'
    if image4 == urls[8]:
        f4 = 'app/static/pu.jpg'
    if image4 == urls[9]:
        f4 = 'app/static/taylor.jpg'




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

    pic = session['pic']
    idpic = str(username + pic[11:-4] + f4[11:-4] + partname)
    swap.main(image1=pic, image2=f4, username=username, OVERLAY_POINTS=OVERLAY_POINTS, part=partname)
    session['pic'] = '/tmp/' + idpic + '.jpg'
    # exchange_part.set_pic('/tmp/' + idpic + '.jpg')
    return redirect(url_for('exchange_part_process'))
