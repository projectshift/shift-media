from unittest import mock, TestCase
from nose.plugins.attrib import attr

from shiftmedia import utils


@attr('storage')
class UtilsTests(TestCase):
    """ Unit tests for utility functions """

    @attr('zzz')
    def test_normalize_extension_when_known(self):
        """ Normalizing file extension """
        extension = 'JPEG'
        self.assertEquals('jpg', utils.normalize_extension(extension))

    @attr('zzz')
    def test_normalize_extension_returns_original_for_unknown(self):
        """ Normalize extension returns original when unknown """
        extension = 'UNKNOWN'
        self.assertEquals('unknown', utils.normalize_extension(extension))











