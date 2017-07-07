from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, PIL
from PIL import Image, JpegImagePlugin
from shiftmedia.resizer import Resizer
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('resizer', 'autocrop','integration')
class AutocropIntegrationTests(TestCase, LocalStorageTestHelpers):
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

    # test assets
    files = dict(
        vertical=dict(file='original_vertical.jpg', size=(248, 768)),
        horizontal=dict(file='original_horizontal.jpg', size=(768, 248)),
        square=dict(file='original_square.jpg', size=(700, 700)),
        orientation=dict(file='bad_orientation.jpg', size=(2448, 3264))
    )

    # ------------------------------------------------------------------------
    # Image manipulation tests: to fit
    # ------------------------------------------------------------------------

    def test_integration_fit_no_upscale_smaller_original(self):
        """ INTEGRATION: Fit, no upscale, src smaller """
        img = self.files['vertical'] #248x768
        filename = img['file']
        target_size = '3000x1000'
        mode = Resizer.RESIZE_TO_FIT
        upscale = False
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(img['size'][0], result.size[0])
        self.assertEquals(img['size'][1], result.size[1])
        # result.show()

    def test_integration_fit_no_upscale_one_side_smaller(self):
        """ INTEGRATION: Fit, no upscale, one side smaller"""
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '300x500'
        mode = Resizer.RESIZE_TO_FIT
        upscale = False
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(161, result.size[0])
        self.assertEquals(500, result.size[1])
        # result.show()

    def test_integration_fit_no_upscale_bigger_original(self):
        """ INTEGRATION: Fit, no upscale, original bigger"""
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '200x300'
        mode = Resizer.RESIZE_TO_FIT
        upscale = False
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(96, result.size[0])
        self.assertEquals(300, result.size[1])
        # result.show()

    def test_integration_fit_upscale_smaller_original(self):
        """ INTEGRATION: Fit, upscale, original smaller """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '300x900'
        mode = Resizer.RESIZE_TO_FIT
        upscale = True
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(290, result.size[0])
        self.assertEquals(900, result.size[1])
        # result.show()

    def test_integration_fit_upscale_one_side_smaller(self):
        """ INTEGRATION: Fit, upscale, one side smaller """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '300x500'
        mode = Resizer.RESIZE_TO_FIT
        upscale = True
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(161, result.size[0])
        self.assertEquals(500, result.size[1])
        # result.show()

    def test_integration_fit_upscale_bigger_original(self):
        """ INTEGRATION: Fit, upscale, original bigger """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '200x300'
        mode = Resizer.RESIZE_TO_FIT
        upscale = True
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(96, result.size[0])
        self.assertEquals(300, result.size[1])
        # result.show()

    # ------------------------------------------------------------------------
    # Image manipulation tests: to fill
    # ------------------------------------------------------------------------

    def test_integration_fill_no_upscale_smaller_original(self):
        """ Fill, no upscale, src smaller """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '2000x3000'
        mode = Resizer.RESIZE_TO_FILL
        upscale = False
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(248, result.size[0])
        self.assertEquals(768, result.size[1])
        # result.show()

    def test_integration_fill_no_upscale_one_side_smaller(self):
        """ Fill, no upscale, one side smaller """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '150x900'
        mode = Resizer.RESIZE_TO_FILL
        upscale = False
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(150, result.size[0])
        self.assertEquals(768, result.size[1])
        # result.show()

    def test_integration_fill_no_upscale_bigger_original(self):
        """ Fill, no upscale, original bigger """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '200x100'
        mode = Resizer.RESIZE_TO_FILL
        upscale = False
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(200, result.size[0])
        self.assertEquals(100, result.size[1])
        # result.show()

    def test_integration_fill_upscale_original_smaller(self):
        """ Fill, upscale, original smaller """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '300x1000'
        mode = Resizer.RESIZE_TO_FILL
        upscale = True
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(300, result.size[0])
        self.assertEquals(1000, result.size[1])
        # result.show()

    def test_integration_fill_upscale_one_side_smaller(self):
        """ Fill, upscale, one side smaller """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '200x1500'
        mode = Resizer.RESIZE_TO_FILL
        upscale = True
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(200, result.size[0])
        self.assertEquals(1500, result.size[1])
        # result.show()

    def test_integration_fill_upscale_original_bigger(self):
        """ Fill, upscale, original bigger """
        img = self.files['vertical']  # 248x768
        filename = img['file']
        target_size = '200x300'
        mode = Resizer.RESIZE_TO_FILL
        upscale = True
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(200, result.size[0])
        self.assertEquals(300, result.size[1])
        # result.show()

    # ------------------------------------------------------------------------
    # Image manipulation tests: GIF animations
    # ------------------------------------------------------------------------

    def test_resize_jpeg(self):
        """ Resizing JPG image """
        filename = 'original_vertical.jpg'
        target_size = '200x300'
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        dst = os.path.join(self.tmp_path, filename)
        result = Resizer.auto_crop(src, dst, target_size)
        self.assertTrue(os.path.isfile(result))
        out = Image.open(result)
        self.assertEquals(200, out.size[0])
        self.assertEquals(300, out.size[1])
        # out.show()

    def test_resize_single_frame_gif(self):
        """ Resizing single frame GIF image """
        filename = 'single_frame.gif'
        target_size = '50x50'
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        dst = os.path.join(self.tmp_path, filename)
        result = Resizer.auto_crop(src, dst, target_size)
        self.assertTrue(os.path.isfile(result))
        out = Image.open(result)
        self.assertEquals(50, out.size[0])
        self.assertEquals(50, out.size[1])
        # out.show()

    def test_resize_animated_gif(self):
        """ Resizing animated GIF image """
        filename = 'test.gif'
        target_size = '100x100'
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        dst = os.path.join(self.tmp_path, filename)
        result = Resizer.auto_crop(src, dst, target_size)
        self.assertTrue(os.path.isfile(result))
        out = Image.open(result)
        self.assertEquals(100, out.size[0])
        self.assertEquals(100, out.size[1])
        self.assertTrue(out.info['duration'] > 0)
        # out.show()

    def test_resize_with_conversion(self):
        """ Resizing image with format conversion"""
        filename = 'single_frame.gif'
        target_size = '50x50'
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        dst = os.path.join(self.tmp_path, filename)
        result = Resizer.auto_crop(src, dst, target_size, format='JPEG')
        self.assertTrue(os.path.isfile(result))
        out = Image.open(result)
        self.assertEquals(50, out.size[0])
        self.assertEquals(50, out.size[1])
        self.assertTrue(isinstance(out, JpegImagePlugin.JpegImageFile))
        # out.show()

    # ------------------------------------------------------------------------
    # Image manipulation tests: Rotation metadata
    # ------------------------------------------------------------------------

    def test_integration_fit_no_upscale_smaller_original2(self):
        """ INTEGRATION: Fit, no upscale, src smaller """
        img = self.files['orientation'] #248x768
        filename = img['file']
        target_size = '300x100'
        mode = Resizer.RESIZE_TO_FIT
        upscale = False
        self.prepare_uploads()
        src = os.path.join(self.upload_path, filename)
        result = Resizer.auto_crop_img(src, target_size, mode, upscale)
        self.assertEquals(75, result.size[0])
        self.assertEquals(100, result.size[1])
        result.show()