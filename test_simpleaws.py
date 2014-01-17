#! /usr/bin/env python

import sys
import boto
import uuid
from boto.s3.key import Key
from simpleaws import simpleaws
import settings

def upload_test_files(username, bucket=None, bucketname=None, keys=None):

    if not bucket:
        s3 = boto.connect_s3(keys['AWS_ACCESS_KEY'], keys['AWS_SECRET_ACCESS_KEY'])
        bucket = s3.get_bucket(bucketname)

    def percent_cb(complete, total):
        sys.stdout.write('.')
        sys.stdout.flush()

    k = Key(bucket)
    k.key = username + "/test.mp4"
    k.set_contents_from_filename('test.mp4', cb=percent_cb, num_cb=10)
    return k

def main():

    simpleaws.set_keys(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_ACCESS_KEY)

    print "Connecting: "
    success = simpleaws.connect()
    if success:
        print "Success!\n"
    else:
        print "Failure. :(\n"
        return

    bucketname = str(uuid.uuid4())
    print "Creating bucket: " + bucketname + ": "
    bucket = simpleaws.create_bucket(bucketname)
    print "Success!\n"

    username = 'user' + str(uuid.uuid4())
    print "Creating user: " + username
    user = simpleaws.create_user(username, bucketname)
    print "Success! \n"

    print "Getting user keys: "
    keys = simpleaws.get_user_keys(username)
    print keys
    print "\n"

    print "Uploading test files to new bucket as " + username + ":"
    contents = upload_test_files(username, bucket, bucketname, keys)
    print ''
    print "Success!"
    print "File uploaded here: " + contents.generate_url(expires_in=300)
    print "\n"

    print "Moving bucket to CloudFront"
    print simpleaws.move_bucket_to_cloudfront(bucketname)

    print "Backing up bucket"
    print simpleaws.backup_bucket(bucketname)

if __name__ == "__main__":
    main()
