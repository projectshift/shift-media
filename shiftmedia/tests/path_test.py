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
        with assert_raises(x.ConfigurationException):
            PathBuilder(DefaultConfig.SECRET_KEY)

    def test_generate_signature(self):
        """ Generating hash signature"""
        filename = 'example.jpg'
        id = utils.generate_id('jpg')
        pb = PathBuilder('12345')
        signature1 = pb.generate_signature(id, filename)
        signature2 = pb.generate_signature(id, filename)
        self.assertEquals(signature1, signature2)

    def test_auto_crop_filename_generator_raises_on_bad_size(self):
        """ Auto crop filename generator raises exception on bad size """
        params = dict(
            id=utils.generate_id('jpg'),
            size='100xCRAP',
            factor='fill',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        pb = PathBuilder('12345')
        with assert_raises(x.InvalidArgumentException):
            pb.get_auto_crop_filename(**params)

    def test_auto_crop_filename_generator_raises_on_bad_factor(self):
        """ Auto crop filename generator raises exception on bad crop factor """
        params = dict(
            id=utils.generate_id('jpg'),
            size='100x200',
            factor='CRAP',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        pb = PathBuilder('12345')
        with assert_raises(x.InvalidArgumentException):
            pb.get_auto_crop_filename(**params)

    def test_auto_crop_filename_generator_raises_on_bad_quality(self):
        """ Auto crop filename generator raises exception on bad quality """
        params = dict(
            id=utils.generate_id('jpg'),
            size='100x200',
            factor='fit',
            output_format='jpg',
            upscale=True,
            quality="CRAP"
        )
        pb = PathBuilder('12345')
        with assert_raises(x.InvalidArgumentException):
            pb.get_auto_crop_filename(**params)

    def test_create_auto_crop_filename(self):
        """ Creating filename for auto crop"""
        params = dict(
            id=utils.generate_id('jpg'),
            size='100x200',
            factor='fill',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        pb = PathBuilder('12345')
        filename = pb.get_auto_crop_filename(**params)
        start = '100x200-fill-80-upscale'
        self.assertTrue(filename.startswith(start))

    def test_manual_crop_filename_generator_raises_on_bad_sample_size(self):
        """ Manual crop filename generator raises on bad sample size"""
        params = dict(
            id=utils.generate_id('jpg'),
            sample_size='200xCRAP',
            target_size='100x200',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        pb = PathBuilder('12345')
        with assert_raises(x.InvalidArgumentException):
            pb.get_manual_crop_filename(**params)

    def test_manual_crop_filename_generator_raises_on_bad_target_size(self):
        """ Manual crop filename generator raises on bad target size"""
        params = dict(
            id=utils.generate_id('jpg'),
            sample_size='200x400',
            target_size='100xCRAP',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        pb = PathBuilder('12345')
        with assert_raises(x.InvalidArgumentException):
            pb.get_manual_crop_filename(**params)

    def test_manual_crop_filename_generator_raises_on_bad_sizes(self):
        """ Manual crop filename generator raises on disproportional sizes """
        params = dict(
            id=utils.generate_id('jpg'),
            sample_size='200x300',
            target_size='100x200',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        pb = PathBuilder('12345')
        with assert_raises(x.InvalidArgumentException):
            pb.get_manual_crop_filename(**params)

    def test_manual_crop_filename_generator_raises_on_quality(self):
        """ Manual crop filename generator raises on bad  quality """
        params = dict(
            id=utils.generate_id('jpg'),
            sample_size='200x400',
            target_size='100x200',
            output_format='jpg',
            upscale=True,
            quality='CRAP'
        )
        pb = PathBuilder('12345')
        with assert_raises(x.InvalidArgumentException):
            pb.get_manual_crop_filename(**params)

    def test_generate_manual_crop_filename(self):
        """ Generating manual crop filename"""
        params = dict(
            id=utils.generate_id('jpg'),
            sample_size='200x400',
            target_size='100x200',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        pb = PathBuilder('12345')
        filename = pb.get_manual_crop_filename(**params)
        start = '200x400-100x200-80-upscale'
        self.assertTrue(filename.startswith(start))

    def test_validate_signature(self):
        """ Validating signature contained within filename  """
        auto_id = utils.generate_id('jpg')
        auto_params = dict(
            id=auto_id,
            size='100x200',
            factor='fill',
            output_format='jpg',
            upscale=True,
            quality=80
        )
        manual_id = utils.generate_id('jpg')
        manual_params = dict(
            id=manual_id,
            sample_size='200x400',
            target_size='100x200',
            output_format='jpg',
            upscale=True,
            quality=80
        )

        pb = PathBuilder('12345')
        auto = pb.get_auto_crop_filename(**auto_params)
        manual = pb.get_manual_crop_filename(**manual_params)
        bad = manual.split('-')
        bad[4] = 'ZZZ' + bad[4]
        bad = '-'.join(bad)
        self.assertTrue(pb.validate_signature(auto_id, auto))
        self.assertTrue(pb.validate_signature(manual_id, manual))
        self.assertFalse(pb.validate_signature(manual_id, bad))
















