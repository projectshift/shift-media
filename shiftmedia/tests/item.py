from unittest import mock, TestCase
from nose.plugins.attrib import attr

import uuid, os, boto3
from shiftmedia import Item
from config.local import LocalConfig


class ItemTests(TestCase):
    """ Media item entity tests """

    def setUp(self):
        super().setUp()

    def get_config(self):
        """ Returns aws config for testing """
        return dict(
            aws_access_key_id=LocalConfig.AWS_IAM_KEY_ID,
            aws_secret_access_key=LocalConfig.AWS_IAM_ACCESS_SECRET
        )

    def test_can_instantiate(self):
        """ Can instantiate media item entity """
        item = Item()
        self.assertIsInstance(item, Item)
        self.assertIsInstance(item.id, uuid.UUID)

    @attr('boto')
    def test_can_boto(self):
        """ Can list S3 buckets with boto """
        s3 = boto3.resource('s3', **self.get_config())
        for bucket in s3.buckets.all():
            print(bucket.name)

        print(list(s3.buckets.all()))

    # @attr('boto')
    # def test_can_upload_to_s3(self):
    #     """ Can upload stuff to s3 """
    #     filename = 'test.jpg'
    #     path = os.path.realpath(os.path.dirname(__file__))
    #     path = os.path.join(path, 'test_assets', filename)
    #
    #     s3 = boto3.resource('s3', **self.get_config())
    #     bucket = s3.Bucket(LocalConfig.AWS_S3_BUCKET)
    #
    #     with open(path, 'rb') as data:
    #         result = bucket.put_object(Key='my_example_file.jpg', Body=data)
    #         print('RESULT', result)




