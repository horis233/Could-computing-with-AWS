"""
faceswap can put facial features from one face onto another.

Usage: faceswap [options] <image1> <image2>

Options:
    -v --version     show the version.
    -h --help        show usage message.
"""
import os
from flask import session
from app import webapp
from app.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import boto3
import cv2
import dlib
import numpy as np

'''
class urlvar:
    url = None


class errorvar:
    error_msg = None


def set_error(error_msg):
    errorvar.error_msg = error_msg


def get_error():
    return errorvar.error_msg
    
'''


__version__ = '1.0'



PREDICTOR_PATH = "/tmp/shape_predictor_68_face_landmarks.dat"

SCALE_FACTOR = 1
FEATHER_AMOUNT = 11

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))

ALIGN_POINTS = (LEFT_BROW_POINTS + RIGHT_EYE_POINTS + LEFT_EYE_POINTS +
                RIGHT_BROW_POINTS + NOSE_POINTS + MOUTH_POINTS)

COLOUR_CORRECT_BLUR_FRAC = 0.6



dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


class Error(Exception):
    pass


@webapp.route('/get_landmark')
def get_landmarks(im):
    detector = dlib.get_frontal_face_detector()

    predictor = dlib.shape_predictor(PREDICTOR_PATH)
    try:
        rects = detector(im, 1)
        if len(rects) > 1:
            raise Error('Your picture has too many faces')
        if len(rects) == 0:
            raise Error('There is no face in your picture')
    except Error as error_catch:
        session['error_msg'] = str(error_catch)
        # set_error(str(error_catch))
        #print(get_error())

    else:
        return np.matrix([[p.x, p.y] for p in predictor(im, rects[0]).parts()])


def annotate_landmarks(im, landmarks):
    im = im.copy()
    for idx, point in enumerate(landmarks):
        pos = (point[0, 0], point[0, 1])
        cv2.putText(im, str(idx), pos,
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.4,
                    color=(0, 0, 255))
        cv2.circle(im, pos, 3, color=(0, 255, 255))
    return im


def draw_convex_hull(im, points, color):
    points = cv2.convexHull(points)
    cv2.fillConvexPoly(im, points, color=color)


def get_face_mask(im, landmarks, OVERLAY_POINTS):
    im = np.zeros(im.shape[:2], dtype=np.float64)

    for group in OVERLAY_POINTS:
        draw_convex_hull(im,
                         landmarks[group],
                         color=1)

    im = np.array([im, im, im]).transpose((1, 2, 0))

    im = (cv2.GaussianBlur(im, (FEATHER_AMOUNT, FEATHER_AMOUNT), 0) > 0) * 1.0
    im = cv2.GaussianBlur(im, (FEATHER_AMOUNT, FEATHER_AMOUNT), 0)

    return im


def transformation_from_points(points1, points2):
    points1 = points1.astype(np.float64)
    points2 = points2.astype(np.float64)

    c1 = np.mean(points1, axis=0)
    c2 = np.mean(points2, axis=0)
    points1 -= c1
    points2 -= c2

    s1 = np.std(points1)
    s2 = np.std(points2)
    points1 /= s1
    points2 /= s2

    U, S, Vt = np.linalg.svd(points1.T * points2)

    R = (U * Vt).T

    return np.vstack([np.hstack(((s2 / s1) * R,
                                 c2.T - (s2 / s1) * R * c1.T)),
                      np.matrix([0., 0., 1.])])


def read_im_and_landmarks(fname):
    im = cv2.imread(fname, cv2.IMREAD_COLOR)
    im = cv2.resize(im, (im.shape[1] * SCALE_FACTOR,
                         im.shape[0] * SCALE_FACTOR))
    s = get_landmarks(im)

    return im, s


def warp_im(im, M, dshape):
    output_im = np.zeros(dshape, dtype=im.dtype)
    cv2.warpAffine(im,
                   M[:2],
                   (dshape[1], dshape[0]),
                   dst=output_im,
                   borderMode=cv2.BORDER_TRANSPARENT,
                   flags=cv2.WARP_INVERSE_MAP)
    return output_im


def correct_colours(im1, im2, landmarks1):
    blur_amount = COLOUR_CORRECT_BLUR_FRAC * np.linalg.norm(
        np.mean(landmarks1[LEFT_EYE_POINTS], axis=0) -
        np.mean(landmarks1[RIGHT_EYE_POINTS], axis=0))
    blur_amount = int(blur_amount)
    if blur_amount % 2 == 0:
        blur_amount += 1
    im1_blur = cv2.GaussianBlur(im1, (blur_amount, blur_amount), 0)
    im2_blur = cv2.GaussianBlur(im2, (blur_amount, blur_amount), 0)

    im2_blur += (128 * (im2_blur <= 1.0)).astype(im2_blur.dtype)

    return (im2.astype(np.float64) * im1_blur.astype(np.float64) /
            im2_blur.astype(np.float64))


def main(image1, image2, username, OVERLAY_POINTS, part):

    if os.path.isfile('/tmp/shape_predictor_68_face_landmarks.dat') is False:
        s3dat = boto3.resource('s3',
                               aws_access_key_id=AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3dat.Object('a3test2', 'shape_predictor_68_face_landmarks.dat').download_file(
            '/tmp/shape_predictor_68_face_landmarks.dat')

    table = dynamodb.Table('Images')
    im1, landmarks1 = read_im_and_landmarks(image1)
    im2, landmarks2 = read_im_and_landmarks(image2)
    if session['error_msg'] is not None:
        return
    M = transformation_from_points(landmarks1[ALIGN_POINTS], landmarks2[ALIGN_POINTS])

    mask = get_face_mask(im2, landmarks2, OVERLAY_POINTS)
    warped_mask = warp_im(mask, M, im1.shape)
    combined_mask = np.max([get_face_mask(im1, landmarks1, OVERLAY_POINTS), warped_mask],
                           axis=0)
    warped_im2 = warp_im(im2, M, im1.shape)
    warped_corrected_im2 = correct_colours(im1, warped_im2, landmarks1)

    output_im = im1 * (1.0 - combined_mask) + warped_corrected_im2 * combined_mask

    idpic = str(username + image1[11:-4] + image2[11:-4] + part)

    cv2.imwrite('/tmp/' + idpic + '.jpg', output_im)

    with open('/tmp/' + idpic + '.jpg', "rb") as image:
        s3.upload_fileobj(image, 'a3test2', idpic)

    '''
    session['url'] = url
    tablesession.update_item(
        Key={
            'username': username,
        },
        UpdateExpression="set url = :u",
        ExpressionAttributeValues={
            ':u': url,
        },
    )
    '''
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': 'a3test2',
            'Key': idpic
        }
    )
    session['url'] = url
    table.put_item(
        Item={
            'username': username,
            'image': idpic,
        }
    )

'''
def set_url(url):
    urlvar.url = url


def get_url():
    return urlvar.url
'''
