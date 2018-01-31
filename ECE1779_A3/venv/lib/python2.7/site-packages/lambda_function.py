import cv2
import dlib
import numpy as np
import os
import boto3
import botocore
import urllib

#print os.environ

# Setup AWS access and S3 buckets
S3OUTBUCKET = os.environ.get('S3OUTBUCKET')
S3INBUCKET = os.environ.get('S3INBUCKET')

def lambda_handler(event, context):
	print "OpenCV version=", cv2.__version__
	print "np version=", np.__version__
	print "context=", context
	print "event=", event
	
	bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'])
	print key

	return "yay, it works!"

if __name__ == "__main__":
	lambda_handler(42, 42)
