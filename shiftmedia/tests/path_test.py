from unittest import mock, TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_raises

from shiftmedia import utils
from shiftmedia.paths import PathBuilder
from shiftmedia.config.default import DefaultConfig
from shiftmedia import exceptions as x


@attr('paths')
class PathBuilderTests(TestCase):
    """ Unit tests for path builder functionality """

    def test_instantiate_path_builder(self):
        """ Instantiating path builder """
        pb = PathBuilder(secret_key='12345')
        self.assertIsInstance(pb, PathBuilder)

    def test_path_builder_requires_configured_secret_key(self):
        """ Path builder forbids default secret key """
        with assert_raises(x.ConfigurationException) as exception:
            PathBuilder(DefaultConfig.SECRET_KEY)

    def test_generate_signature(self):
        """ Generating hash signature"""
        filename = 'example.jpg'
        id = utils.generate_id('jpg')
        pb = PathBuilder('12345')
        signature1 = pb.generate_signature(id, filename)
        signature2 = pb.generate_signature(id, filename)
        self.assertEquals(signature1, signature2)

    # def test_validate_signature(self):
    #     """ Generating filename signature"""
    #     raise Exception('Not implemented')
    #
    @attr('xxx')
    def test_create_auto_resize_url(self):
        """ Creating URL for auto resizing"""
        params = dict(
            id=utils.generate_id('jpg'),
            size='100x200',
            factor='fill',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        pb = PathBuilder('12345')
        filename = pb.get_autocrop_filename(**params)







    #
    # def test_create_manual_crop_url(self):
    #     """ Create manual crop url """
    #     pass













