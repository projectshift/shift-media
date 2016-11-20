from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, shutil
from config.local import LocalConfig
from shiftmedia import BackendLocal
from shiftmedia import Storage
from shiftmedia.resizer import Resizer
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('resizer')
class StorageTests(TestCase, LocalStorageTestHelpers):
    """ Storage service tests """

    def setUp(self):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        # self.clean()
        super().tearDown()

    # ------------------------------------------------------------------------
    # Resize to fit math
    # ------------------------------------------------------------------------

    def test_fit_no_upscale_smaller_original(self):
        """ Fit, no upscale, src smaller """
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        src = (100, 300)
        dst = (200, 400)
        upscale = False
        result = resizer.get_ratio(src, dst,mode=mode, upscale=upscale)
        self.assertEquals(src, result['size'])
        self.assertEquals((0,0), result['position'])

    def test_fit_no_upscale_one_side_smaller(self):
        """ Fit, no upscale, one side smaller"""
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        src = (100, 300)
        dst = (50, 400)
        upscale = False
        result = resizer.get_ratio(src, dst,mode=mode, upscale=upscale)
        self.assertEquals((50, 150), result['size'])
        self.assertEquals((0, 0), result['position'])

    def test_fit_no_upscale_bigger_original(self):
        """ Fit, no upscale, original bigger"""
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        src = (2000, 4000)
        dst = (1000, 1500)
        upscale = False
        result = resizer.get_ratio(src, dst,mode=mode, upscale=upscale)
        self.assertEquals((750, 1500), result['size'])
        self.assertEquals((0, 0), result['position'])

    def test_fit_upscale_smaller_original(self):
        """ Fit, upscale, original smaller """
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        src = (2000, 1000)
        dst = (3500, 3000)
        upscale = True
        result = resizer.get_ratio(src, dst, mode=mode, upscale=upscale)
        self.assertEquals((3500, 1750), result['size'])
        self.assertEquals((0, 0), result['position'])

    def test_fit_upscale_one_side_smaller(self):
        """ Fit, upscale, one side smaller """
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        src = (5000, 2200)
        dst = (3500, 3000)
        upscale = True
        result = resizer.get_ratio(src, dst, mode=mode, upscale=upscale)
        self.assertEquals((3500, 1540), result['size'])
        self.assertEquals((0, 0), result['position'])

    def test_fit_upscale_bigger_original(self):
        """ Fit, upscale, original bigger """
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        src = (5000, 3000)
        dst = (1000, 1500)
        upscale = True
        result = resizer.get_ratio(src, dst, mode=mode, upscale=upscale)
        self.assertEquals((1000, 600), result['size'])
        self.assertEquals((0, 0), result['position'])

    # ------------------------------------------------------------------------
    # Resize to fill math
    # ------------------------------------------------------------------------

    def test_fill_no_upscale_smaller_original(self):
        """ Fill, no upscale, src smaller """
        resizer = Resizer
        algo = resizer.RESIZE_SAMPLE
        mode = resizer.RESIZE_TO_FILL
        src = (1000, 3000)
        dst = (2000, 4000)
        upscale = False
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals(src, result['size'])
        self.assertEquals((0, 0), result['position'])

    def test_fill_no_upscale_one_side_smaller(self):
        """ Fill, no upscale, one side smaller """
        resizer = Resizer
        algo = resizer.RESIZE_SAMPLE
        mode = resizer.RESIZE_TO_FILL
        src = (2000, 3000)
        dst = (3000, 2000)
        upscale = False
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((2000, 2000), result['size'])
        self.assertEquals((0, 500), result['position'])

    def test_fill_no_upscale_bigger_original_risize_original(self):
        """ Fill, no upscale, original bigger - resize original algo """
        resizer = Resizer
        algo = resizer.RESIZE_ORIGINAL
        mode = resizer.RESIZE_TO_FILL
        src = (2000, 3000)
        dst = (1000, 2000)
        upscale = False
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((1500, 2000), result['size'])
        self.assertEquals((250, 0), result['position'])

    def test_fill_no_upscale_bigger_original_risize_sample(self):
        """ Fill, no upscale, original bigger - resize sample algo """
        resizer = Resizer
        algo = resizer.RESIZE_SAMPLE
        mode = resizer.RESIZE_TO_FILL
        src = (2000, 3000)
        dst = (1000, 2000)
        upscale = False
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((1500, 3000), result['size'])
        self.assertEquals((250, 0), result['position'])

    def test_fill_upscale_original_smaller_risize_original(self):
        """ Fill, upscale, original smaller - resize original algo """
        resizer = Resizer
        algo = resizer.RESIZE_ORIGINAL
        mode = resizer.RESIZE_TO_FILL
        src = (2000, 1000)
        dst = (4000, 3000)
        upscale = True
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((6000, 3000), result['size'])
        self.assertEquals((1000, 0), result['position'])

    def test_fill_upscale_original_smaller_risize_sample(self):
        """ Fill, upscale, original smaller - resize sample algo """
        resizer = Resizer
        algo = resizer.RESIZE_SAMPLE
        mode = resizer.RESIZE_TO_FILL
        src = (2000, 1000)
        dst = (4000, 3000)
        upscale = True
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((1333, 1000), result['size'])
        self.assertEquals((334, 0), result['position'])

    def test_fill_upscale_one_side_smaller_risize_sample(self):
        """ Fill, upscale, one side smaller - resize sample algo """
        resizer = Resizer
        algo = resizer.RESIZE_SAMPLE
        mode = resizer.RESIZE_TO_FILL
        src = (5000, 2000)
        dst = (4000, 3000)
        upscale = True
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((2666, 2000), result['size'])
        self.assertEquals((1167, 0), result['position'])

    def test_fill_upscale_one_side_smaller_risize_original(self):
        """ Fill, upscale, one side smaller - resize original algo """
        resizer = Resizer
        algo = resizer.RESIZE_ORIGINAL
        mode = resizer.RESIZE_TO_FILL
        src = (4500, 2000)
        dst = (4000, 3000)
        upscale = True
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((6750, 3000), result['size'])
        self.assertEquals((1375, 0), result['position'])

    def test_fill_upscale_original_bigger_risize_original(self):
        """ Fill, upscale, original bigger - resize original algo """
        resizer = Resizer
        algo = resizer.RESIZE_ORIGINAL
        mode = resizer.RESIZE_TO_FILL
        src = (4000, 3000)
        dst = (2000, 1000)
        upscale = True
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((2000, 1500), result['size'])
        self.assertEquals((0, 250), result['position'])

    def test_fill_upscale_original_bigger_risize_sample(self):
        """ Fill, upscale, original bigger - resize sample algo """
        resizer = Resizer
        algo = resizer.RESIZE_SAMPLE
        mode = resizer.RESIZE_TO_FILL
        src = (4000, 3000)
        dst = (2000, 1000)
        upscale = True
        result = resizer.get_ratio(src, dst, mode, algo, upscale)
        self.assertEquals((1333, 1000), result['size'])
        self.assertEquals((334, 0), result['position'])

    # ------------------------------------------------------------------------
    # Image manipulation tests
    # ------------------------------------------------------------------------

    def get_image_data_with_pil(self):
        """ Open a local image with PIL """
        self.prepare_uploads()
        path = os.path.join(self.upload_path, 'original_horizontal.jpg')
        from PIL import Image
        img = Image.open(path)
        img.thumbnail((1000, 1000))
        # img.show()

        self.assertEquals('JPEG', img.format)
        self.assertEquals('RGB', img.mode)

    @attr('xxx')
    def test_can_resize_image(self):
        """ Resizing an image """
        filename = 'original_vertical.jpg'  # 248x768
        target_size = '100x200'
        algo = Resizer.RESIZE_ORIGINAL
        mode = Resizer.RESIZE_TO_FILL
        upscale = True
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.resize(src, target_size, mode, algo, upscale)
        result.show()













