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
    # Tests
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

    def calculate_resize_ratio(self):
        """ Calculating resize ratio """
        dsts = dict(
            horizontal1=(500,200),
            horizontal2=(700,40),
            vertical1=(200,500),
            vertical2=(40,700),
            square=(300,300)
        )
        srcs=dict(
            horizontal=(4000, 1500),
            vertical=(1500, 4000),
            square=(3000, 3000),
            upscale=(30, 10),
        )

        print('\n')
        hr = '-' * 40

        for src in srcs.keys():
            head = 'SRC {} ({}x{})\n' + hr
            print(head.format(src.upper(), srcs[src][0], srcs[src][1], hr))

            for dst in dsts.keys():
                ratio = Resizer.get_ratio(srcs[src], dsts[dst])

                row = 'DST {} ({}x{}): '
                row = row.format(dst.upper(), dsts[dst][0], dsts[dst][1])

                # ratio = [str(x) for x in Resizer.getRatio(*params)]
                # print(row, ratio[0] +'x'+ ratio[1])

                print(row, ratio)

            print('\n')

    def return_src_if_smaller_than_dst_without_upscale(self):
        """ No upscale returns original if smaller than resize """
        resizer = Resizer
        result = Resizer.get_ratio((100, 100), (200,200), upscale=False)
        self.assertEquals((100,100), result['size'])
        self.assertEquals((0,0), result['position'])

    def upscaling_to_fit(self):
        """ Can upscale smaller src to fit dst """
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        result = resizer.get_ratio(
            src=(100, 100),
            dst=(300, 200),
            mode=mode,
            upscale=True
        )

        self.assertEquals((200, 200), result['size'])
        self.assertEquals((0,0), result['position'])

    def calculate_to_fit_if_one_side_is_shorter(self):
        """ Calculating to-fit size if one src side is shorter than dst"""
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        result = resizer.get_ratio(src=(200, 400), dst=(300, 200), mode=mode)
        self.assertEquals((100, 200), result['size'])
        self.assertEquals((0,0), result['position'])

    def calculate_to_fit_if_src_larger_than_dst(self):
        """ Calculating to-fit size if src is larger than dst"""
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        result = resizer.get_ratio(src=(400, 800), dst=(200, 200), mode=mode)
        self.assertEquals((100,200), result['size'])
        self.assertEquals((0,0), result['position'])

    def calculate_to_fill_if_one_side_is_shorter(self):
        """ Calculating to-fit size if one src side is shorter than dst"""
        resizer = Resizer
        mode = resizer.RESIZE_TO_FIT
        result = resizer.get_ratio((),(),mode=mode)

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















