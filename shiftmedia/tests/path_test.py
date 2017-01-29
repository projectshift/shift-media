from unittest import mock, TestCase
from nose.plugins.attrib import attr

from shiftmedia.path import PathBuilder


@attr('paths')
class PathBuilderTests(TestCase):
    """ Unit tests for path builder functionality """

    def test_instantiate_path_builder(self):
        """ Instantiating path builder """
        paths = PathBuilder()
        self.assertIsInstance(paths, PathBuilder)

    def test_create_auto_resize_url(self):
        """ Creating URL for auto resizing"""
        pass

    def test_create_manual_crop_url(self):
        """ Create manual crop url """
        pass













