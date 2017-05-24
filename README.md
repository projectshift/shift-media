# shift-media

A library for handling user-generated media files. It uses AWS S3 as storage backend for files. It is assumed that you are not going to server your media from your application but instead let S3 handle the heavy lifting.

## Installation

Image manipulation functionality will require Pillow library and there might be some
quirks with `zlib` and `libjpeg` on MacOS that will get in the way. See [this StackOverflow thread](http://stackoverflow.com/questions/34631806/fail-during-installation-of-pillow-python-module-in-linux)
on how to install the libs.


## Setting up S3

Setting up S3 involves creating an IAM user and granting it proper permissions as well as creating and configuring a bucket to store and serve your files.

### Create IAM user

Go to your AWS Management Console and Select "Identity & Access Management" and create a user. This will generate security credentials that you can download. Make note of this as it will be required to configure media storage.

We are now gonna configure S3 access permissions for the user, but before we do, you might want to consider creating a group and assigning permissions to the group, rather than specific user. The benefit of this is permissions reuse - you can later on add and remove users to/from group and not worry about configuring each one user individually. If you decided to use a group - go ahead and create one and then add user to it.

Now go to the user or group you created and attach an inline policy:

```
{
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "arn:aws:s3:::*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::your-bucket-name-here",
                "arn:aws:s3:::your-bucket-name-here/*"
            ]
        }
    ]
}
```

This will allow to list all buckets the user has access to as well as full access to `your-bucket-name-here` bucket.

### Allow access to ElasticTranscoder

If you will transcode your videos with Elastic transcoder, you might want to reuse the same IAM user in your application.
You will need to create a pipeline in ElasticTranscoder that will write into your bucket and allow the user to use this pipeline, use transcoding preset and create transcoding. Here is an example of such policy:

```yml
        {
            "Effect": "Allow",
            "Action": [
                "elastictranscoder:Read*",
                "elastictranscoder:List*",
                "elastictranscoder:*Job",
                "sns:List*"
            ],
            "Resource": [
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:job/*",
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:preset/*",
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:pipeline/<pipeline_id>",
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:pipeline/<pipeline_id>",
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:pipeline/<pipeline_id>"
            ]
        }
```

Here is the full policy listing updated wit htranscoder access:

```yml
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "arn:aws:s3:::*"
        },
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::your-bucket-name-here",
                "arn:aws:s3:::your-bucket-name-here/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "elastictranscoder:Read*",
                "elastictranscoder:List*",
                "elastictranscoder:*Job",
                "sns:List*"
            ],
            "Resource": [
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:job/*",
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:preset/*",
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:pipeline/<pipeline_id>",
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:pipeline/<pipeline_id>",
                "arn:aws:elastictranscoder:<aws_region>:<aws_account_id>:pipeline/<pipeline_id>"
            ]
        }
    ]
}

```


### Create a public bucket

Go to AWS S3 console and create a new bucket that we'll use to store our media files. The bucket will need to be made public since we are to serve static files from S3 directly, so go bucket properties, select permissions section and apply following policy:

```
{
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name-here/*",
	        "Principal": {
      		  "AWS": [
		          "*"
        		]
		      }
        }
    ]
}
```


### On-the-fly resizing with S3

The workflow for on-the-fly resizing is this:

  * User requests an image resize from the bucket
  * The bucket returns a 404
  * A special bucket policy is applied to redirect 404s back to the app
  * The app parses the resize url and validates signature
  * If valid, app creates downloads the original from the bucket and creates resize
  * The app puts resize back to the bucket and redirects back to original url requested
  * On subsequent requests the resize is already in the bucket and will be served from there

To configure this workflow you must enable static website hosting in bucket properties editor and apply the following routing rules:

```xml
<RoutingRules>
    <RoutingRule>
        <Condition>
            <KeyPrefixEquals/>
            <HttpErrorCodeReturnedEquals>404</HttpErrorCodeReturnedEquals>
        </Condition>
        <Redirect>
            <Protocol>http</Protocol>
            <HostName>your-host-name.com</HostName>
        </Redirect>
    </RoutingRule>
</RoutingRules>
```  

On the other side, you must configure your app have an endpoint that recognizes the request. Here is an example for flask:

```python
from flask import Flask
from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app = Flask(__name__)
app.url_map.converters['regex'] = RegexConverter

@app.route('/<regex("[\w/]{36}/[^/]*/\d*x\d*-[a-z]*-\d{1,2}-[a-z]*-[a-z0-9]{32}.[a-z]*"):path>')
def example(path):
    url = 'http://bucket-name.s3-website-eu-west-1.amazonaws.com/'
    url+= path
    storage.create_resize(url)
    return redirect(url)
```
  



### Troubleshooting: Pillow fails to install on MacOS

If pillow fails to install with this message:

```
ValueError: jpeg is required unless explicitly disabled using --disable-jpeg, aborting
```

Which means lack of jpeg support, you should install it with homebrew first:

```
brew install jpeg
pip install pillow
```







