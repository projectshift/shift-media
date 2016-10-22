from unittest import mock, TestCase
from nose.plugins.attrib import attr

import os, shutil
from config.local import LocalConfig
from shiftmedia import BackendLocal
from shiftmedia import Storage
from shiftmedia.resizer import Resizer
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('storage')
class StorageTests(TestCase, LocalStorageTestHelpers):
    """ Storage service tests """

    def setUp(self):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        self.clean()
        super().tearDown()


    # ------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------

    def test_instantiate_storage(self):
        """ Instantiating storage """
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        self.assertIsInstance(storage, Storage)

    def test_getting_tmp_creates_directory(self):
        """ Can create local temp upon getting """
        shutil.rmtree(self.tmp_path)
        storage = Storage(self.config, mock.MagicMock())
        storage.tmp
        self.assertTrue(os.path.exists(self.tmp_path))

    def test_put_file(self):
        """ Put uploaded file to storage """
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        self.prepare_uploads()
        filepath = os.path.join(self.upload_path, 'test.png')
        id = storage.put(filepath)
        self.assertFalse(os.path.exists(filepath))

    def test_delete_file_by_id(self):
        """ Deleting file from storage by id """
        id = '123'
        backend = mock.MagicMock()
        storage = Storage(self.config, backend)
        storage.delete(id)
        backend.delete.assert_called_with(id)

    # ------------------------------------------------------
    # Resizer tests
    # ------------------------------------------------------

    def test_get_image_data_with_pil(self):
        """ Open a local image with PIL """
        self.prepare_uploads()
        path = os.path.join(self.upload_path, 'original_horizontal.jpg')
        from PIL import Image
        img = Image.open(path)
        img.thumbnail((1000, 1000))
        img.show()

        self.assertEquals('JPEG', img.format)
        self.assertEquals('RGB', img.mode)

    @attr('xxx')
    def test_calculate_resize_ratio(self):
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
                ratio = Resizer.getRatio(srcs[src], dsts[dst])

                row = 'DST {} ({}x{}): '
                row = row.format(dst.upper(), dsts[dst][0], dsts[dst][1])

                # ratio = [str(x) for x in Resizer.getRatio(*params)]
                # print(row, ratio[0] +'x'+ ratio[1])

                print(row, ratio)

            print('\n')
















