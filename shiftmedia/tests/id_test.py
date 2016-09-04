from unittest import mock, TestCase
from nose.plugins.attrib import attr

import uuid, os, boto3
from shiftmedia import Id
from config.local import LocalConfig


@attr('ids')
class IdTests(TestCase):
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
        """ Can instantiate ID value object """
        id = Id()
        self.assertIsInstance(id, Id)

    def test_can_get_as_string(self):
        """ Getting uuid as string """
        id = str(Id())
        self.assertIsInstance(id, str)
        id = id.split('-')
        self.assertEquals(5, len(id))

    def test_can_get_storage_path(self):
        """ Getting id as storage path """
        id = Id()
        path = id.get_storage_path()
        print(path)




