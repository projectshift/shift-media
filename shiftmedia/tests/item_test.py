from unittest import mock, TestCase
from nose.plugins.attrib import attr

import uuid, os, boto3
from shiftmedia import Item


class ItemTests(TestCase):
    """ Media item entity tests """

    def setUp(self, app=None):
        super().setUp()

    def test_can_instantiate(self):
        """ Can instantiate media item entity """
        item = Item()
        self.assertIsInstance(item, Item)
        self.assertIsInstance(item.id, uuid.UUID)

    @attr('boto')
    def test_can_boto(self):
        """ Can list S3 buckets with boto """
        s3 = boto3.resource('s3')
        for bucket in s3.buckets.all():
            print(bucket.name)

    @attr('boto')
    def test_can_upload_to_s3(self):
        """ Can upload stuff to s3 """
        filename = 'test.jpg'
        path = os.path.realpath(os.path.dirname(__file__))
        path = os.path.join(path, 'test_assets', filename)

        s3 = boto3.resource('s3')
        bucket = s3.Bucket('example-shiftmedia-bucket')

        with open(path, 'rb') as data:
            result = bucket.put_object(Key='my_example_file.jpg', Body=data)
            print('RESULT', result)




