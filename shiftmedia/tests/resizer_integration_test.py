from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, shutil
from config.local import LocalConfig
from shiftmedia import BackendLocal
from shiftmedia import Storage
from shiftmedia.resizer import Resizer
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('resizer', 'integration')
class StorageTests(TestCase, LocalStorageTestHelpers):
    """
    Image resizer integration tests
    These will resize actual images
    """
    def setUp(self):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        # self.clean()
        super().tearDown()

    files = dict(
        vertical='original_vertical.jpg',  # 248x768
        horizontal='original_horizontal.jpg',  # 768x248
        square='original_square.jpg',  # 700x700
    )

    # ------------------------------------------------------------------------
    # Image manipulation tests: to fit
    # ------------------------------------------------------------------------

    @attr('xxx')
    def test_integration_fit_no_upscale_smaller_original(self):
        """ INTEGRATION: Fit, no upscale, src smaller """
        filename = self.files['vertical']
        target_size = '300x1000'
        mode = Resizer.RESIZE_TO_FIT
        algo = Resizer.RESIZE_SAMPLE
        upscale = False
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.resize(src, target_size, mode, algo, upscale)
        # result.show()


    def test_integration_fit_no_upscale_one_side_smaller(self):
        """ INTEGRATION: Fit, no upscale, one side smaller"""
        pass


    def test_integration_fit_no_upscale_bigger_original(self):
        """ INTEGRATION: Fit, no upscale, original bigger"""
        pass


    def test_integration_fit_upscale_smaller_original(self):
        """ INTEGRATION: Fit, upscale, original smaller """
        pass


    def test_integration_fit_upscale_one_side_smaller(self):
        """ INTEGRATION: Fit, upscale, one side smaller """
        pass


    def test_integration_fit_upscale_bigger_original(self):
        """ INTEGRATION: Fit, upscale, original bigger """
        pass

    # ------------------------------------------------------------------------
    # Image manipulation tests: to fill
    # ------------------------------------------------------------------------


    def test_integration_fill_no_upscale_smaller_original(self):
        """ Fill, no upscale, src smaller """
        pass


    def test_integration_fill_no_upscale_one_side_smaller(self):
        """ Fill, no upscale, one side smaller """
        pass


    def test_integration_fill_no_upscale_bigger_original_risize_original(self):
        """ Fill, no upscale, original bigger - resize original algo """
        pass


    def test_integration_fill_no_upscale_bigger_original_risize_sample(self):
        """ Fill, no upscale, original bigger - resize sample algo """
        pass


    def test_integration_fill_upscale_original_smaller_risize_original(self):
        """ Fill, upscale, original smaller - resize original algo """
        pass


    def test_integration_fill_upscale_original_smaller_risize_sample(self):
        """ Fill, upscale, original smaller - resize sample algo """
        pass


    def test_integration_fill_upscale_one_side_smaller_risize_sample(self):
        """ Fill, upscale, one side smaller - resize sample algo """
        pass


    def test_integration_fill_upscale_one_side_smaller_risize_original(self):
        """ Fill, upscale, one side smaller - resize original algo """
        pass


    def test_integration_fill_upscale_original_bigger_risize_original(self):
        """ Fill, upscale, original bigger - resize original algo """
        pass


    def test_integration_fill_upscale_original_bigger_risize_sample(self):
        """ Fill, upscale, original bigger - resize sample algo """
        pass










