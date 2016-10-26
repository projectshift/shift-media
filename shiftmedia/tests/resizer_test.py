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

    def test_get_image_data_with_pil(self):
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

    def test_return_src_if_smaller_than_dst_without_upscale(self):
        """ No upscale returns original if smaller than resize """
        resizer = Resizer
        result = Resizer.get_ratio((100, 100), (200,200), upscale=False)
        self.assertEquals((100,100), result['size'])
        self.assertEquals((0,0), result['position'])

    def test_calculate_to_fit_if_one_side_is_shorter(self):
        """ Calculating to-fit size if one src side is shorter """
        resizer = Resizer
        mode = resizer.CROP_TO_FIT
        result = resizer.get_ratio(src=(200, 400), dst=(300, 200), mode=mode)
        self.assertEquals((100, 200), result['size'])
        self.assertEquals((0,0), result['position'])

    def test_calculate_to_fit_is_src_larger_than_dst(self):
        """ Calculating to-fit size if src is larger than dst"""
        resizer = Resizer
        mode = resizer.CROP_TO_FIT
        result = resizer.get_ratio(src=(400, 800), dst=(200, 200), mode=mode)
        self.assertEquals((100,200), result['size'])
        self.assertEquals((0,0), result['position'])






















