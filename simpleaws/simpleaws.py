"""
Simple AWS

An idiot-proof way to make a public S3 based-service.

Supports S3, Cloudfront and STS.

"""
import boto
from boto.s3.connection import Location
from boto.s3.lifecycle import Lifecycle, Transition, Rule

import string
import uuid

global iam
global s3
global cloudfront
global connected

S3_USER_POLICY_TEMPLATE = """{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:PutObjectAclVersion",
            "s3:GetObject",
            "s3:GetObjectVersion",
            "s3:DeleteObject",
            "s3:DeleteObjectVersion"
         ],
         "Resource":"arn:aws:s3:::BUCKET_NAME/USER_NAME/*"
      },
      {
         "Effect":"Allow",
         "Action":[
            "s3:ListBucket",
            "s3:GetBucketLocation",
            "s3:ListAllMyBuckets"
         ],
         "Resource":"arn:aws:s3:::BUCKET_NAME"
      }
   ]
}
"""

connected = False
AWS_ACCESS_KEY = ''
AWS_SECRET_ACCESS_KEY = ''

iam = None
s3 = None
cloudfront = None

def set_keys(AWS_ACCESS_KEY_VAR, AWS_SECRET_ACCESS_KEY_VAR):
    global AWS_ACCESS_KEY
    global AWS_SECRET_ACCESS_KEY

    AWS_ACCESS_KEY = AWS_ACCESS_KEY_VAR
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY_VAR

    return True

def connect():

    global connected
    global AWS_ACCESS_KEY
    global AWS_SECRET_ACCESS_KEY

    global iam
    global s3
    global cloudfront

    if not connected:
        iam = boto.connect_iam(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
        s3 = boto.connect_s3(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
        cloudfront = boto.connect_cloudfront(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
        connected = True

    return connected

def create_user(username, bucketname):
    connect()

    def create_retry(username, bucketname, tries):

        if tries is 0:
            print "SOMETHING WENT HORRIBLY WRONG"
            return None

        try:
            response = iam.create_user(username)
            user = response.user
            policy_json = S3_USER_POLICY_TEMPLATE.replace('BUCKET_NAME', bucketname).replace('USER_NAME', username)
            response = iam.put_user_policy(user_name=username, policy_name=bucketname + "_" + username, policy_json=policy_json)
            return user

        except Exception, e:
            return create_retry(username + '-' + str(uuid.uuid4())[0:8], bucketname, tries-1)

    return create_retry(username, bucketname, 5)

def get_user_keys(username):
    connect()

    response = iam.create_access_key(username)
    access_key = response.access_key_id
    secret_key = response.secret_access_key
     
    return {
            'AWS_ACCESS_KEY': access_key, 
            'AWS_SECRET_ACCESS_KEY': secret_key
            }

def create_bucket(bucketname, location=None):
    connect()

    def create_retry(bucketname, location, tries):

        if tries is 0:
            return None

        try:
            if location:
                return s3.create_bucket(bucketname, location)
            else: 
                return s3.create_bucket(bucketname)
        except Exception, e:
            return create_retry(bucketname + '-' + str(uuid.uuid4()), location, tries-1)

    return create_retry(bucketname, location, 5)

def backup_bucket(bucketname):
    connect()

    bucket = s3.get_bucket(bucketname)
    to_glacier = Transition(days=1, storage_class='GLACIER')
    rule = Rule('ruleid', '/', 'Enabled', transition=to_glacier)
    lifecycle = Lifecycle()
    lifecycle.append(rule)
    bucket.configure_lifecycle(lifecycle)

    return True

def move_bucket_to_cloudfront(bucketname):
    connect()

    origin = boto.cloudfront.origin.S3Origin(bucketname + '.s3.amazonaws.com')
    distro = cloudfront.create_distribution(origin=origin, enabled=True, comment=bucketname + " Distribution")
    return distro.domain_name
