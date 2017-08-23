# USAGE
# This python script is launched without any arguements
# 
# Logic Flow
# connect to AWS S3 bucket - credentials held in the .boto configuration file
# 
# Enter an infinite while loop while:
# 		getting list of objects in the temporary-incoming-images bucket
#		for each object retrieved it is downloaded, passed to the deep dreaming code, then deleted from the temporary-incoming-images bucket 
#		Then both the before & after images are uploaded to the S3 buckets deepnightmare-before and deepnightmare-after respecitively
#		The loops then sleeps for 10 seconds before checking for more new images
#

# import the necessary packages
from batcountry import BatCountry
from PIL import Image
import numpy as np
import os
import sys
import time
import logging
import hashlib

os.environ["BOTO_CONFIG"] = ".boto"
import boto
from boto.s3.key import Key
LOGGING = True
VERBOSITY = False
DEBUGGING = True

if LOGGING:
	logging.basicConfig(filename='deepnightmare.log',level=logging.DEBUG)

def mydebugmsg(msg):
	if LOGGING:
		logging.debug(msg)
	if DEBUGGING:
		print (msg)
	return

#
# creates a hash value based on the content of the input file
#

def create_hash(file):
	BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

	md5 = hashlib.md5()
	sha1 = hashlib.sha1()

	with open(file, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			md5.update(data)
			sha1.update(data)

	mydebugmsg("MD5: {0}".format(md5.hexdigest()))
	mydebugmsg("SHA1: {0}".format(sha1.hexdigest()))
	
	return md5.hexdigest()

# 
# Functio to create thumbnail images
#

def create_thumbnail(image_path, image_keyname, dest_bucket):

	mydebugmsg("creating thumbail for " + image_path)
	
	image_thumbnail_name = image_keyname + "-thumbnail.jpg" 
	image_thumbnail_path = "thumbnails/" + image_thumbnail_name 

	size = 256, 256
	im = Image.open(image_path)
	im.thumbnail(size)
	im.save(image_thumbnail_path, "JPEG")

	dest_bucket = dest_bucket.new_key(image_thumbnail_name)
	dest_bucket.set_contents_from_filename(image_thumbnail_path)
	dest_bucket.set_acl('public-read')

	return


#
# this is the function that calls the bat-country code to dream
#

def dream_that_image(before, after, layer, seed, filehash, iteration):
	
	# dreaming...
	mydebugmsg("Dreaming dream #" + str(iteration) )
	mydebugmsg("before = [" + before + "]")
	mydebugmsg("after  = [" + after + "]")

	bc 			= BatCountry(DREAMMODEL)
	features 	= bc.prepare_guide(Image.open(seed), end=layer)
	image 		= bc.dream(np.float32(Image.open(before)), end=layer,
		iter_n=20, objective_fn=BatCountry.guided_objective,
		objective_features=features, verbose=VERBOSITY)
	
	bc.cleanup()

	#
	# write the output image to file
	#
	
	result = Image.fromarray(np.uint8(image))
	result.save(after)

	#
	# Save both the input image and output image to S3 using the MD5 hash of the original file content as the key name
	#

	keyname = filehash + ".jpg"
	key 	= beforebucket.new_key(keyname)

	key.set_contents_from_filename(before)
	key.set_acl('public-read')

	mydebugmsg ("new key name = [" + keyname + "]")

	create_thumbnail(before, keyname, before_thumbnails_bucket)

	#
	# keyname should look like hashvalue.1.jpg 
	#

	keyname = filehash + "." + str(iteration) + ".jpg"
	key 	= afterbucket.new_key(keyname)

	key.set_contents_from_filename(after)
	key.set_acl('public-read')

	mydebugmsg ("new key name = [" + keyname + "]")

	create_thumbnail(after, keyname, after_thumbnails_bucket)

	mydebugmsg ("------------------------------------------")
	return

#
# Main body of the code
#

mydebugmsg("started debugging")

DOWNLOAD_PATH 	= "images-in/"
OUTPUT_PATH 	= "images-out/"
DREAMMODEL 		= "/usr/local/caffe/models/bvlc_googlenet"
SEEDPATH 		= "images-seed/"
LAYER1 			= "conv2/3x3"
LAYER2 			= "inception_4c/5x5_reduce"
LAYER3 			= ""
SEED1 			= "angryface.jpg"
SEED2 			= ""
SEED3 			= ""

temp_bucket_name				= "temporary-incoming-images"
before_bucket_name 				= "deepnightmare-before"
after_bucket_name 				= "deepnightmare-after"
before_thumbnails_bucket_name 	= "deepnightmare-before-thumbnails"
after_thumbnails_bucket_name 	= "deepnightmare-after-thumbnails"

#boto.set_stream_logger('boto')
s3 = boto.connect_s3()

tempbucket 					= s3.get_bucket(temp_bucket_name)
beforebucket 				= s3.get_bucket(before_bucket_name)
afterbucket 				= s3.get_bucket(after_bucket_name)
before_thumbnails_bucket 	= s3.get_bucket(before_thumbnails_bucket_name)
after_thumbnails_bucket 	= s3.get_bucket(after_thumbnails_bucket_name)


while True:
	for photo in tempbucket.list():

		#
		# for each new photo in the temp bucket, download it to the local folder images-in then delete from the bucket
		# once downloaded - run the deep nightmare routine against the downloaded file
		# once completed - the before image is uploaded to the deepnightmare-before bucket and the after image to the deepnightmare-after bucket
		#

		photo_name 			= str(photo.key)
		photo_before_path 	= DOWNLOAD_PATH + photo_name
		photo_after_path 	= OUTPUT_PATH + photo_name
		
		# retrieve image from S3 to local storage and create hashkey for the file

		photo.get_contents_to_filename(photo_before_path)
		myhash = create_hash(photo_before_path)

		mydebugmsg ("retrieved key = <" + photo_name + ">")
		mydebugmsg ("save path     = <" + photo_after_path + ">")
		mydebugmsg ("deleting photo  <" + photo_name + "> from S3")
		photo.delete()
		
		SEED = SEEDPATH + SEED1
		
		dream_that_image (photo_before_path, photo_after_path, LAYER1, SEED, myhash, 1)
		dream_that_image (photo_before_path, photo_after_path, LAYER2, SEED, myhash, 2)
		mydebugmsg ("done dreaming, onto the next image")
		
	time.sleep(10)


