# shift-media

A library for handling user-generated media files. It uses AWS S3 as storage backend for files. It is assumed that you are not going to server your media from your application but instead let S3 handle the heavy lifting.

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


### Create a bucket




