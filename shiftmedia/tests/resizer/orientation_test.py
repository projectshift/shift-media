from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, PIL
from PIL import Image, JpegImagePlugin
from shiftmedia.resizer import Resizer
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('resizer', 'orientation', 'integration')
class OrientationTests(TestCase, LocalStorageTestHelpers):
    """
    Image resizer orientation fixer tests
    """
    def setUp(self):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        # self.clean()
        super().tearDown()

    # ------------------------------------------------------------------------
    # Image manipulation tests: to fit
    # ------------------------------------------------------------------------

    def test_orientation_fixer_with_unicode_in_exif(self):
        """ REGRESSION: Images with unicode Exif data can be rotated """
        path = os.path.join(
            os.getcwd(),
            'shiftmedia',
            'tests',
            'test_assets',
            'unicode_exif.jpg'
        )

        img = Image.open(path)
        img, exif = Resizer.fix_orientation(img)


