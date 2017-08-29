# DeepNightmare

This "Deep Nightmare" application utilises deep dreaming image manipulation techniques to produce warped and freaky images based on an input image of a person's face
After trying several other packages and failing I settled on using bat-country https://github.com/jrosebr1/bat-country/edit/master/batcountry/batcountry.py

This is part of a multi-app solution with a Raspberry Pi running a photo booth. Captured photos are sent to S3 which will be picked up and manipulated using this application running on my local machine. The final application is a flask web application running on Pivotal Cloud Foundry which will show an album of all images stored.

## Installation

The bootstrap.sh DID work, but when I tried to rebuild again I was getting pip errors "cannot import name IncompleteRead" - I solved this by deleting /usr/local/python2.7/dist-packages/resource*
BUT THEN, the application bombs out, so I move those folders back and the application now works (but pip is broken)

Important - the version of bat-country that is installed using pip is old and out of date. The base functionality works but when you try to specify a new guide-image a syntax error is thrown. "variable nH is used before assigned"
To fix this I downloaded the latest copy of batcountry.py from the git repository and manually replaced the pip installed version - /usr/local/lib/python2.7/dist-packages/batcountry/batcountry.py

Important - the installation of caffe is missing the model file required by bat-country - bvlc_googlenet.caffemodel 
you will find this in the folder named models and this file should be copied to /usr/local/caffe/models/bvlc_googlenet to avoid errors

These changes could/should be added to the bootstrap.sh file. Update - I have amended the bootstrap.sh file to copy these files to their proper locations

## Data Flow

The application scans the S3 bucket "temporary-incoming-images" for new images. When found, the image is downloaded and parsed twice - using different layers but the same seed image.
The image is deleted from the temp bucket, and once parsing has been completed the before image and 2 * after images are uploaded to the "deepnightmare-before" and "Deepnightmare-after" buckets
The application then generates thumbnail versions of each image and uploads to the thumbnail buckets.

In early versions of the code I used the original file name throughout - appending layer names & seed image names to the after image names. This would lead to problems if different incoming images shared the same name. Also the layer name would often include a '/' which would then lead to folders being created in the S3 buckets. So to solve these problems I run a MD5 hash against the incoming image content and then all subsequent images use the hash value as part of the name.

## Notes



# bat-country
<img src="initial_images/fear_and_loathing/fal_01.jpg?raw=true" style="max-width: 300px;"/><br/>
<img src="examples/output/fear_and_loathing/conv2_3x3_fal_01.jpg?raw=true" style="max-width: 300px;"/>
> We can't stop here, this is bat country. &mdash; Raoul Duke

The `bat-country` package is an **easy to use**, **highly extendible**, **lightweight Python module** for **inceptionism** and **deep dreaming** with Convolutional Neural Networks and Caffe. My contributions here are honestly pretty minimal. All the real research has been done by the [Google Research Team](http://googleresearch.blogspot.com/2015/06/inceptionism-going-deeper-into-neural.html) &mdash; I'm simply taking the [IPython Notebook](https://github.com/google/deepdream/blob/master/dream.ipynb), turning it into a Python module, while keeping in mind the importance of extensibility, such as custom step functions.

If you're looking for a more advanced CNN visualization tool, check out Justin Johnson's [cnn-vis](https://github.com/jcjohnson/cnn-vis) library.

## Installation
The `bat-country` packages requires [Caffe, an open-source CNN implementation from Berkeley](http://caffe.berkeleyvision.org/), to be already installed on your system. I detail the steps required to get Caffe up and running on your system in the [official bat-country release post](http://www.pyimagesearch.com/2015/07/06/bat-country-an-extendible-lightweight-python-package-for-deep-dreaming-with-caffe-and-convolutional-neural-networks/). An excellent alternative is to use the [Docker image](https://github.com/VISIONAI/clouddream) provided by Tomasz of Vision.ai. Using the Docker image will get you up and running quite painlessly.

After you have Caffe setup and working, `bat-country` is a breeze to install. Just use pip:

<pre>$ pip install bat-country</pre>

You can also install `bat-country` by pulling down the repository and `setup.py`:

<pre>$ git clone https://github.com/jrosebr1/bat-country.git
$ pip install -r requirements.txt
$ python setup.py install</pre>

## A simple example
As I mentioned, one of the goals of `bat-country` is simplicity. Provided you have already installed Caffe and `bat-country` on your system, it only takes 3 lines of Python code to generate a deep dream/inceptionism image:

<pre># we can't stop here...
bc = BatCountry("caffe/models/bvlc_googlenet")
image = bc.dream(np.float32(Image.open("/path/to/image.jpg")))
bc.cleanup()</pre>

After executing this code, you can then take the `image` returned by the `dream` method and write it to file:

<pre>result = Image.fromarray(np.uint8(image))
result.save("/path/to/output.jpg")</pre>

And that's it!

For more information on `bat-country`, along with more code examples, head over to the the official announcement post on the PyImageSearch blog:

[http://www.pyimagesearch.com/2015/07/06/bat-country-an-extendible-lightweight-python-package-for-deep-dreaming-with-caffe-and-convolutional-neural-networks/](http://www.pyimagesearch.com/2015/07/06/bat-country-an-extendible-lightweight-python-package-for-deep-dreaming-with-caffe-and-convolutional-neural-networks/)

## Guided dreaming
Google has also demonstrated that it's possible to *guide* your dreaming process by supplying a *seed image*. This method passes your input image through the network in a similar manner, but this time using your seed image to guide the output.

Using `bat-country`, it's just as easy to perform *guided dreaming* as *deep dreaming*. Here's some quick sample code:

<pre>bc = BatCountry(args.base_model)
features = bc.prepare_guide(Image.open(args.guide_image), end=args.layer)
image = bc.dream(np.float32(Image.open(args.image)), end=args.layer,
	iter_n=20, objective_fn=BatCountry.guided_objective,
	objective_features=features,)
bc.cleanup()</pre>

What's nice about this approach is that I "guide" what the output image looks like. Here I use a seed image of Vincent van Gogh's Starry Night and apply to an image of clouds:

<img src="docs/images/clouds_and_starry_night_example.jpg?raw=true" style="max-width: 500px;"/>

As you can see, the output cloud image after applying guided dreaming appears to mimic many of the brush strokes of Van Gogh's painting:

<img src="examples/output/seeded/clouds_and_starry_night.jpg?raw=true" style="max-width: 500px;"/>

Here's another example, this time using a seed image of an antelope:

<img src="docs/images/clouds_and_antelope_example.jpg?raw=true" style="max-width: 500px;"/>

You can read more about guided dreaming, plus view more example images here:

[http://www.pyimagesearch.com/2015/07/13/generating-art-with-guided-deep-dreaming/](http://www.pyimagesearch.com/2015/07/13/generating-art-with-guided-deep-dreaming/)

## Some visual examples
Below are a few example images generated using the `bat-country` package:

<img src="initial_images/fear_and_loathing/fal_03.jpg?raw=true" style="max-width: 500px;"/><br/>
<img src="examples/output/fear_and_loathing/inception_4c_output_fal_03.jpg?raw=true" style="max-width: 500px;"/><br/><br/>

<img src="initial_images/the_matrix/matrix_01.jpg?raw=true" style="max-width: 500px;"/><br/>
<img src="examples/output/the_matrix/conv2_3x3_matrix_01.jpg?raw=true" style="max-width: 500px;"/><br/><br/>

<img src="initial_images/jurassic_park/jp_06.jpg?raw=true" style="max-width: 500px;"/><br/>
<img src="examples/output/jurassic_park/conv2_3x3_jp_06.jpg?raw=true" style="max-width: 500px;"/><br/><br/>

<img src="initial_images/jurassic_park/jp_01.jpg?raw=true" style="max-width: 500px;"/><br/>
<img src="examples/output/jurassic_park/conv2_3x3_jp_01.jpg?raw=true" style="max-width: 500px;"/><br/><br/>

<img src="initial_images/jurassic_park/jp_03.jpg?raw=true" style="max-width: 500px;"/><br/>
<img src="examples/output/jurassic_park/conv2_3x3_jp_03.jpg?raw=true" style="max-width: 500px;"/><br/><br/>