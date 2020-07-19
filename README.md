# shift-media

**Please note: this is in very early alpha. Not ready for any use.**

A library for handling user-generated media files. It uses AWS S3 as storage backend for files. It is assumed that you are not going to serve your media from your application but instead let S3 handle the heavy lifting.

## Installation

Image manipulation functionality will require Pillow library and there might be some
quirks with `zlib` and `libjpeg` on MacOS that will get in the way. See [this StackOverflow thread](http://stackoverflow.com/questions/34631806/fail-during-installation-of-pillow-python-module-in-linux)
on how to install the libs.


## Setting up S3

Setting up S3 involves creating an IAM user and granting it proper permissions as well as creating and configuring a bucket to store and serve your files.

### Create IAM user

Go to your AWS Management Console and Select "Identity & Access Management" and create a user. This will generate security credentials that you can download. Make note of this as it will be required to configure media storage.

We are now gonna configure S3 access permissions for the user, but before we do, you might want to consider creating a group and assigning permissions to the group, rather than specific user. The benefit of this is permissions reuse - you can later add and remove users to/from this group and not worry about configuring each one user individually. If you decided to use a group - go ahead and create one and then add the user to it.

Now go to the user or group you created and attach an inline policy:

```json
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

Here is the full policy listing updated with transcoder access:

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

Go to AWS S3 console and create a new bucket that we'll use to store our media files. The bucket will need to be made public since we are to serve static files from S3 directly, so go to bucket properties, select permissions section and apply following policy:

```
{
    "Version": "2012-10-17",
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
  * If valid, app downloads the original from the bucket and creates resize
  * The app puts resize back to the bucket and redirects back to original url requested
  * On subsequent requests the resize will already be in the bucket and will be served from there

To configure this workflow you must enable static website hosting in bucket properties editor and apply the routing below. It is important to set redirect code to 302 so the browsers don't cache that redirect which can cause an infinite loop. 

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
            <ReplaceKeyPrefixWith>media/</ReplaceKeyPrefixWith>
            <HttpRedirectCode>302</HttpRedirectCode>		
        </Redirect>
    </RoutingRule>
</RoutingRules>
```  

On the other side, you must configure your app to have an endpoint that recognizes the request. Here is an example for flask that will work with both local media storage and s3 media storage including when served by flask dev server. Notice that this time, after the resize has been created we issue a 301 redirect.

```python

@app.route('/media/<path:path>/')
def media_endpoint(path=None):
    """
    Static media endpoint
    Used as a flask view to perform several actions: in dev environment
    serves static files if they exist. otherwise (for any environment)
    attempts to create a dynamic o-the-fly resize
    :param path: str, path to an original or resize
    :return:
    """
    p = r'[\w/]{36}/[^/]*/\d*x\d*-[a-z]*-\d{1,2}-[a-z]*-[a-z0-9]{32}.[a-z]*'
    if not re.match('/media/{}'.format(p), request.path):
        abort(404)

    # local media storage: serve if exists
    if isinstance(media.backend, BackendLocal):
        local_media_path = os.path.join(os.getcwd(), 'media')
        exists = os.path.isfile(os.path.join(local_media_path, path))

        # ensure app only serves static in dev mode
        if exists and current_app.config.get('ENV') != 'development':
            err = 'This endpoint only works in development. Use a web ' \
                  'server to serve static assets in production.'
            abort(400, err)

        # serve is exists (dev server only)
        if exists:
            cache_timeout = current_app.get_send_file_max_age(path)
            return send_from_directory(
                directory=local_media_path,
                filename=path,
                cache_timeout=cache_timeout
            )

    # otherwise create resize
    try:
        backend_url = media.backend.get_url().rstrip('/')
        url = '{}/{}'.format(backend_url, path)

        # S3: check if exists (important)
        if isinstance(media.backend, BackendS3):
            path = url.replace(media.backend.get_url(), '').lstrip('/')
            exists = media.backend.exists(path)
            if exists:
                return redirect(url, code=301)

        # create new resize and redirect
        media.create_resize(url)

        # redirect to resized version
        return redirect(url, code=301)

    except mx.MediaException:
        pass

    # otherwise not found
    abort(404)
```

## On the fly resizes with HTTPS

If you need to use on-the fly resize functionality in HTTPS environment with a custom domain, there is some extra setup to be done. At the moment static web hosting (that redirects back to app on 404s) only works with HTTP (for custom domains), so no HTTPS support there. However we can put our 'static website' behind a CloudFront distribution:

  * Come up with a subdomain name for your media storage, e.g. media.yourdomain.com
  * For that subdomain create a certificate with CertificateManager in North Virginia region (us-east-1)
  * Set up CloudFront distribution and set the origin to be the url of your static website endpoint (not your s3 bucket url)
  * Set all the caches to zero (we only gonna use CloudFront for SSL termination)
 

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


### Troubleshooting: Too many redirects for resizes after setting up CloudFront

As outlined above the workflow for creating a resize is this: 

  * hit media storage (cloudfront)
  * get forwarder back to app
  * get forwarded back to media storage

The problem here is that the first time we hit cloudfront and the resize is missing, we get redirected to the app (via routing rules) and CloudFront actually caches that redirect.

The workaround at the moment is to disable Cloudfront caching altogether - go and set your cache lifetimes in AWS console to zero. Then invalidate your cahes.





