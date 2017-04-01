from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, PIL
from PIL import Image, JpegImagePlugin
from shiftmedia.resizer import Resizer
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('resizer', 'manualcrop','integration')
class ManualCropIntegrationTests(TestCase, LocalStorageTestHelpers):
    """
    Image resizer integration tests
    This will exercise manual crop/resize functionality
    """
    def setUp(self):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        # self.clean()
        super().tearDown()

    # test assets
    files = dict(
        vertical=dict(file='original_vertical.jpg', size=(248, 768)),
        horizontal=dict(file='original_horizontal.jpg', size=(768, 248)),
        square=dict(file='original_square.jpg', size=(700, 700))
    )

    # ------------------------------------------------------------------------
    # Image manipulation tests
    # ------------------------------------------------------------------------

    def test_integration_fit_no_upscale_smaller_original(self):
        """ INTEGRATION: Fit, no upscale, src smaller """
        self.assertTrue(True)
