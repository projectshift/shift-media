from unittest import mock, TestCase
from nose.plugins.attrib import attr
from nose.tools import assert_raises

import os, boto3
from botocore import exceptions as bx
from PIL import Image
from config.local import LocalConfig
from shiftmedia import BackendS3, utils, PathBuilder, exceptions as x
from shiftmedia.testing.localstorage_testhelpers import LocalStorageTestHelpers


@attr('backend', 's3')
class BackendLocalTests(TestCase, LocalStorageTestHelpers):
    """ Local storage backend tests """

    @property
    def config(self):
        """ Returns dict with credentials  to access s3 test  bucket """
        credentials = dict(
            key_id=LocalConfig.AWS_IAM_KEY_ID,
            access_secret=LocalConfig.AWS_IAM_ACCESS_SECRET,
            bucket=LocalConfig.AWS_S3_BUCKET,

        )
        return credentials

    def setUp(self, app=None):
        super().setUp()

    def tearDown(self):
        """ Clean up after yourself """
        # self.clean()
        # self.clean_s3()
        super().tearDown()

    def clean_s3(self, path=None):
        """
        Recursive delete
        Uses paginator to fetch S3 objects, that deletes them in chunks
        """
        backend = BackendS3(**self.config)
        backend.recursive_delete()

    # ------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------

    def test_can_instantiate_backend(self):
        """ Can instantiate backend  """
        backend = BackendS3(**self.config)
        self.assertIsInstance(backend, BackendS3)

    def test_convert_id_to_path(self):
        """ Converting id to path """
        backend = BackendS3(**self.config)
        filename = 'demo-test.tar.gz'
        id = utils.generate_id(filename)
        parts = backend.id_to_path(id)
        self.assertEquals(6, len(parts))
        self.assertEquals(filename, parts[5])

    def test_parse_url(self):
        """ Parsing object url into id and filename """
        filename = 'demo-file.tar.gz'
        backend = BackendS3(**self.config)
        pb = PathBuilder('123456')
        base_url = backend.get_url()
        id = utils.generate_id(filename)
        parts = backend.id_to_path(id)
        path = '/'.join(parts)
        object_url = base_url + '/' + path + '/'
        original = object_url + filename
        crop_filename = pb.get_auto_crop_filename(id, '100x100', 'fit')
        resize = object_url + crop_filename
        result1 = backend.parse_url(original)
        result2 = backend.parse_url(resize)
        self.assertEquals(id, result1[0])
        self.assertEquals(filename, result1[1])
        self.assertEquals(id, result2[0])
        self.assertEquals(crop_filename, result2[1])

    def test_check_existence(self):
        """ Checking object existence"""
        backend = BackendS3(**self.config)
        client = boto3.client('s3', **backend.credentials)
        client.put_object(
            Bucket=backend.bucket_name,
            Key='test-object',
            Body=''
        )
        client.put_object(
            Bucket=backend.bucket_name,
            Key='test-dir/',
            Body=''
        )
        self.assertTrue(backend.exists('test-object'))
        self.assertTrue(backend.exists('test-dir/'))
        self.assertFalse(backend.exists('nonexistent'))

    def test_put_raises_on_nonexistent_file(self):
        """ Put raises exception if source file does not exist """
        backend = BackendS3(**self.config)
        id = utils.generate_id('test.tar.gz')
        with assert_raises(x.LocalFileNotFound):
            backend.put_variant('nonexistent', id, 'random.tar.gz')

    def test_put_file(self):
        """ Put file to storage """
        self.prepare_uploads()
        backend = BackendS3(**self.config)
        uploads = self.upload_path
        src = os.path.join(uploads, 'demo-test.tar.gz')
        id = utils.generate_id('demo-test.tar.gz')
        backend.put(src, id)
        path = '/'.join(backend.id_to_path(id)) + '/demo-test.tar.gz'
        self.assertTrue(backend.exists(path))

    def test_put_file_variant(self):
        """ Put file to storage by filename"""
        self.prepare_uploads()
        backend = BackendS3(**self.config)
        uploads = self.upload_path
        src = os.path.join(uploads, 'demo-test.tar.gz')
        id = utils.generate_id('demo-test.tar.gz')
        backend.put_variant(src, id, 'variant.tar.gz')
        path = '/'.join(backend.id_to_path(id)) + '/variant.tar.gz'
        self.assertTrue(backend.exists(path))

    def test_put_with_sequential_ids(self):
        """ Putting two items in sequence"""
        filename = 'demo-test.tar.gz'
        base_id = utils.generate_id(filename).replace('-' + filename, '')
        id1 = base_id + '1-' + filename
        id2 = base_id + '2-' + filename
        self.prepare_uploads()
        backend = BackendS3(**self.config)
        uploads = self.upload_path
        src = os.path.join(uploads, 'demo-test.tar.gz')
        backend.put_variant(src, id1, 'demo-test.tar.gz')
        backend.put_variant(src, id2, 'demo-test.tar.gz')
        path1 = '/'.join(backend.id_to_path(id1)) + '/demo-test.tar.gz'
        path2 = '/'.join(backend.id_to_path(id2)) + '/demo-test.tar.gz'
        self.assertTrue(backend.exists(path1))
        self.assertTrue(backend.exists(path2))

    def test_put_raises_on_overwriting(self):
        """ Put raises exception on attempt to overwrite existing path """
        self.prepare_uploads()
        backend = BackendS3(**self.config)
        uploads = self.upload_path
        src1 = os.path.join(uploads, 'demo-test.tar.gz')
        src2 = os.path.join(uploads, 'test.jpg')
        id = utils.generate_id('demo-test.tar.gz')
        backend.put_variant(src1, id, 'demo-test.tar.gz')
        with assert_raises(x.FileExists):
            backend.put_variant(src2, id, 'demo-test.tar.gz')

    def test_force_put_to_overwrite_existing(self):
        """ Using force option to overwrite existing file """
        self.prepare_uploads()
        backend = BackendS3(**self.config)
        uploads = self.upload_path
        filename = 'demo-test.tar.gz'
        src1 = os.path.join(uploads, filename)
        src2 = os.path.join(uploads, 'test.jpg')
        id = utils.generate_id(filename)
        backend.put_variant(src1, id, filename)
        backend.put_variant(src2, id, filename, True)

        path = '/'.join(backend.id_to_path(id)) + '/' + filename
        client = boto3.client('s3', **backend.credentials)
        res = client.head_object(Bucket=backend.bucket_name, Key=path)
        self.assertEquals(
            str(os.path.getsize(src2)),
            str(res['ResponseMetadata']['HTTPHeaders']['content-length'])
        )

    def test_guess_content_type(self):
        """ Guess content type for objects when putting to S3 """
        self.prepare_uploads()
        backend = BackendS3(**self.config)

        src = os.path.join(self.upload_path, 'test.jpg')
        id = utils.generate_id('demo.jpg')
        backend.put(src, id, True)

        path = '/'.join(backend.id_to_path(id)) + '/demo.jpg'
        client = boto3.client('s3', **backend.credentials)
        res = client.head_object(
            Bucket=backend.bucket_name,
            Key=path
        )
        headers = res['ResponseMetadata']['HTTPHeaders']
        self.assertEquals('image/jpeg', headers['content-type'])

    def test_delete_file(self):
        """ Deleting file from local storage """
        # put file
        self.prepare_uploads()
        backend = BackendS3(**self.config)
        uploads = self.upload_path
        src = os.path.join(uploads, 'test.tar.gz')

        id1 = utils.generate_id('test.tar.gz')
        backend.put(src, id1)

        # regression testing (only delete what requested)
        id2 = id1.split('-')
        id2[4] += 'ZZZ'
        id2 = '-'.join(id2)

        backend.put(src, id1, True)
        backend.put_variant(src, id1, 'demo.txt')
        backend.put(src, id2, True)
        backend.delete(id1)

        path1 = '/'.join(backend.id_to_path(id1)) + '/test.tar.gz'
        path2 = '/'.join(backend.id_to_path(id1)) + '/demo.txt'
        self.assertFalse(backend.exists(path1))
        self.assertFalse(backend.exists(path2))

        # assume only proper file deleted
        path3 = '/'.join(backend.id_to_path(id2)) + '/test.tar.gz'
        self.assertTrue(backend.exists(path3))

    def test_retrieve_original_to_temp(self):
        """ Retrieving from backend to local temp """
        # put file
        self.prepare_uploads()
        backend = BackendS3(**self.config)
        src = os.path.join(self.upload_path, 'demo-test.tar.gz')
        id = utils.generate_id('demo-test.tar.gz')
        backend.put(src, id)

        # retrieve file
        result = backend.retrieve_original(id, self.tmp_path)
        expected_dst = os.path.join(self.tmp_path, id, 'demo-test.tar.gz')
        self.assertEquals(expected_dst, result)
        self.assertTrue(os.path.exists(expected_dst))


    @attr('xxx')
    def test_clear_variants(self):
        """ Clearing generated variants"""
        self.prepare_uploads()
        backend = BackendS3(**self.config)

        # src1 = os.path.join(self.upload_path, 'demo-test.tar.gz')
        # id1 = utils.generate_id('demo-test.tar.gz')
        # backend.put(src1, id1)
        # backend.put_variant(src1, id1, 'variant1.tar.gz')
        # backend.put_variant(src1, id1, 'variant2.tar.gz')

        # src2 = os.path.join(self.upload_path, 'demo-test.tar.gz')
        # id2 = utils.generate_id('test.jpg')
        # backend.put(src2, id2)
        # backend.put_variant(src2, id2, 'variant1.jpg')
        # backend.put_variant(src2, id2, 'variant2.jpg')

        # self.clean()
        # self.clean_s3()





