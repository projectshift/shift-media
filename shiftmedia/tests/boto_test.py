
from unittest import mock, TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_raises

from shiftmedia import utils
from shiftmedia.paths import PathBuilder
from shiftmedia.config.default import DefaultConfig
from shiftmedia import exceptions as x


@attr('boto')
class BotoTests(TestCase):
    """
    Boto Tests
    This will test AWS services integration with boto3
    """
    # @attr('boto')
    # def test_can_boto(self):
    #     """ Can list S3 buckets with boto """
    #     s3 = boto3.resource('s3', **self.get_config())
    #     for bucket in s3.buckets.all():
    #         print(bucket.name)
    #
    #     print(list(s3.buckets.all()))
    #
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

    pass