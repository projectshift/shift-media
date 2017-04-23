import os, shutil, mimetypes, boto3
from pprint import PrettyPrinter
from abc import ABCMeta, abstractmethod
from botocore import exceptions as bx
from shiftmedia import exceptions as x


class Backend(metaclass=ABCMeta):
    """
    Abstract backend
    This defines methods your backend must implement in order to
    work with media storage
    """
    @abstractmethod
    def __init__(self, url='http://localhost'):
        """
        Backend constructor
        Requires a base storage url to build links.
        :param url: string - base storage url
        """
        self._url = url

    def get_url(self):
        """
        Get URL
        Returns base URL of storage
        """
        return self._url

    @abstractmethod
    def put(self, src, id, force=False):
        """
        Put  file to storage
        Does not require a filename as it will be extracted from provided id.
        Will raise an exception on an attempt to overwrite existing file which
        you can force to ignore.
        """
        pass

    @abstractmethod
    def put_variant(self, src, id, filename, force=False):
        """
        Put file variant to storage
        Save local file in storage under given id and filename. Will raise an
        exception on an attempt to overwrite existing file which you can force
        to ignore.
        """
        pass

    @abstractmethod
    def retrieve_original(self, id, local_path):
        """
        Retrieve original
        Download file original from storage and put to local temp path
        """
        pass

    @abstractmethod
    def delete(self, id):
        """
        Delete
        Remove file from storage by id
        """
        pass

    @abstractmethod
    def parse_url(self, url):
        """
        Parse url
        Processes url to return a tuple of id and filename. This is being used
        when we create dynamic image resizes to retrieve the original based on
        resize filename.
        :param url: string - resize url
        :return: tuple - id and filename
        """
        pass

    @abstractmethod
    def clear_variants(self):
        """
        Clear variants
        Iterates through storage and removes all files that are not originals.
        This is a good way to clear residual files not being used and
        regenerate the once in use.
        :return: Bool
        """
        pass


class BackendLocal(Backend):
    """
    Local backend
    Stores file locally in a directory without transferring to remote storage
    """

    def __init__(self, local_path=None, url='http://localhost'):
        """
        Backend constructor
        Requires a local storage path and base storage url.
        :param local_path: string - path to local temp dir
        :param url: string - base storage url
        """
        super().__init__(url)
        self._path = local_path

    @property
    def path(self):
        """
        Get path
        Returns path to local storage and creates one if necessary
        """
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        return self._path

    def id_to_path(self, id):
        """
        Id to path
        Returns a list of directories extracted from id
        :param id: string, - object id
        :return: list
        """
        parts = id.lower().split('-')[0:5]
        tail = id[len('-'.join(parts)) + 1:]
        parts.append(tail)
        return parts

    def parse_url(self, url):
        """
        Parse url
        Processes url to return a tuple of id and filename. This is being used
        when we create dynamic image resizes to retrieve the original based on
        resize filename.
        :param url: string - resize url
        :return: tuple - id and filename
        """
        url = url.replace(self._url, '')
        url = url.strip('/').lower()
        url = url.split('/')
        id = '-'.join(url[:-1])
        filename = url[-1]
        return id, filename

    def put(self, src, id, force=False):
        """
        Put file to storage
        Does not require a filename as it will be extracted from provided id.
        the resulting path will have following structure:
            3c72aedc/ba25/11e6/569/406c8f413974/file.jpg/file.jpg

        :param src: string - path to source file
        :param id: string - generated id
        :param force: bool - whether to overwrite existing
        :return: string - generated id
        """
        filename = '-'.join(id.split('-')[5:])
        return self.put_variant(src, id, filename, force)

    def put_variant(self, src, id, filename, force=False):
        """
        Put file variant to storage
        Save local file in storage under given id and filename. Will raise an
        exception on an attempt to overwrite existing file which you can force
        to ignore.
        """
        if not os.path.exists(src):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(src))

        parts = self.id_to_path(id)
        dir = os.path.join(self.path, *parts)
        os.makedirs(dir, exist_ok=True)
        dst = os.path.join(self.path, *parts, filename.lower())
        if not force and os.path.exists(dst):
            msg = 'File [' + filename + '] exists under [' + id + ']. '
            msg += 'Use force option to overwrite.'
            raise x.FileExists(msg)
        shutil.copyfile(src, dst)
        return id

    def delete(self, id):
        """
        Delete
        Remove file from storage by id
        """
        id = str(id)
        path = os.path.join(self.path, *id.split('-')[0:5])
        shutil.rmtree(path)
        return True

    def retrieve_original(self, id, local_path):
        """
        Retrieve original
        Download file from storage and put to local temp path
        """
        path = self.id_to_path(id)
        filename = path[5]
        src = os.path.join(self.path, *path, filename)
        dst_dir = os.path.join(local_path, id)
        dst = os.path.join(dst_dir, filename)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)
        shutil.copyfile(src, dst)
        return dst

    def clear_variants(self):
        """
        Clear variants
        Iterates through storage and removes all files that are not originals.
        This is a good way to clear residual files not being used and
        regenerate the once in use.
        :return: Bool
        """
        for subdir, dirs, files in os.walk(self.path):
            for file in files:
                if subdir.endswith(file): continue # skip originals
                path = os.path.join(subdir, file)
                os.remove(path)

        return True


class BackendS3(Backend):
    """
    Amazon S3 backend
    Stores files in an amazon s3 bucket
    """
    def __init__(self, key_id, access_secret, bucket, url='http://localhost'):
        """
        S3 Backend constructor
        Creates an instance of s3 backend, requires credentials to access
        amazon s3 and bucket name.

        :param key_id: string - AWS IAM Key id
        :param access_secret: string - AWS IAM Access secret
        :param bucket: string - AWS S3 bucket name, e.g. 'test-bucket'
        :param url: string - base storage url
        """
        self.bucket_name = bucket
        self.credentials = dict(
            aws_access_key_id=key_id,
            aws_secret_access_key=access_secret,
        )
        super().__init__(url)

    def pp(self, what):
        """ Pretty-prints an object"""
        printer = PrettyPrinter(indent=2)
        printer.pprint(what)

    def id_to_path(self, id):
        """
        Id to path
        Returns a list of directories extracted from id
        :param id: string, - object id
        :return: list
        """
        parts = id.lower().split('-')[0:5]
        tail = id[len('-'.join(parts)) + 1:]
        parts.append(tail)
        return parts

    def parse_url(self, url):
        """
        Parse url
        Processes url to return a tuple of id and filename. This is being used
        when we create dynamic image resizes to retrieve the original based on
        resize filename.
        :param url: string - resize url
        :return: tuple - id and filename
        """
        url = url.replace(self._url, '')
        url = url.strip('/').lower()
        url = url.split('/')
        id = '-'.join(url[:-1])
        filename = url[-1]
        return id, filename

    def exists(self, object):
        """
        Exists
        Checks whether a file or directory/ exists and returns a boolean result.

        Be careful with directories - it might appear that they exist when
        in fact they don't, e.g. /some/path/file.txt existence doesn't
        necessarily mean .some/path exists. Thus it is more helpful to check
        for file existence, i.e. the FULL key existence.

        :param object: string - file or directory/
        :return: bool
        """
        try:
            resource = boto3.resource('s3', **self.credentials)
            resource.Object(self.bucket_name, object).load()
        except bx.ClientError as e:
            if e.response['Error']['Code'] == '404': return False
            else: raise e

        return True

    def recursive_delete(self, path=None):
        """
        Recursive delete
        Deletes all objects recursively under given path. If path is not
        provided, will delete every object in the bucket. Be careful!
        :param path: string - objects starting with this will be deleted
        :return: None
        """
        client = boto3.client('s3', **self.credentials)
        paginator = client.get_paginator('list_objects_v2')
        params = dict(Bucket=self.bucket_name)
        if path: params['Prefix'] = path
        pages = paginator.paginate(**params)

        delete_us = dict(Objects=[])
        bucket = self.bucket_name
        for item in pages.search('Contents'):
            if not item: continue
            delete_us['Objects'].append(dict(Key=item['Key']))

            # flush full page
            if len(delete_us['Objects']) >= 999:
                client.delete_objects(Bucket=bucket, Delete=delete_us)
                delete_us = dict(Objects=[])

        # flush last page
        if len(delete_us['Objects']):
            client.delete_objects(Bucket=bucket, Delete=delete_us)

    def put(self, src, id, force=False, content_type=None, encoding=None):
        """
        Put file to storage
        Does not require a filename as it will be extracted from provided id.
        the resulting path will have following structure:
            3c72aedc/ba25/11e6/569/406c8f413974/file.jpg/file.jpg

        :param src: string - path to source file
        :param id: string - generated id
        :param force: bool - whether to overwrite existing
        :param content_type: string - content/type, guessed if none
        :param encoding: string - content encoding, guessed if none
        :return: string - generated id
        """
        filename = '-'.join(id.split('-')[5:])
        return self.put_variant(
            src,
            id,
            filename,
            force,
            content_type,
            encoding
        )

    def put_variant(
        self,
        src,
        id,
        filename,
        force=False,
        content_type=None,
        encoding=None):
        """
        Put file variant to storage
        Save local file in storage under given id and filename. Will raise an
        exception on an attempt to overwrite existing file which you can force
        to ignore. By default will guess content-type and content-encoding based
        on file extension that you can override to set your own.

        :param src: string - path to local file
        :param id: string - storage object id
        :param filename: string - varian filename
        :param force: bool - whether to overwrite if exists
        :param content_type: string - content/type, guessed if none
        :param encoding: string - content encoding, guessed if none
        :return: string put object id
        """
        if not os.path.exists(src):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(src))

        path = '/'.join(self.id_to_path(id)) + '/' + filename
        if not force and self.exists(path):
            msg = 'File [' + filename + '] exists under [' + id + ']. '
            msg += 'Use force option to overwrite.'
            raise x.FileExists(msg)

        if not content_type or not encoding:
            guessed = mimetypes.guess_type(src)
            content_type = content_type if content_type else guessed[0]
            encoding = encoding if encoding else guessed[1]

        client = boto3.client('s3', **self.credentials)
        with open(src, 'rb') as src:
            params = dict(
                ACL='public-read',
                Bucket=self.bucket_name,
                Key=path,
                Body=src
            )
            if content_type: params['ContentType'] = content_type
            if encoding: params['ContentEncoding'] = encoding
            client.put_object(**params)

        return id

    def delete(self, id):
        """
        Delete
        Remove file from storage by id. Since it searches for the keys
        staring (!) with id, can accept nonexistent ids.
        """
        path = '/'.join(self.id_to_path(id))
        self.recursive_delete(path)

    def retrieve_original(self, id, local_path):
        """
        Retrieve original
        Download file from storage and put to local temp path

        :param id: string - storage object id
        :param local_path: string - local path to download to
        :return: path to local download
        """
        path = self.id_to_path(id)
        filename = path[5]
        dst_dir = os.path.join(local_path, id)
        dst = os.path.join(dst_dir, filename)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)

        filename = '-'.join(id.split('-')[5:])
        src = '/'.join(self.id_to_path(id)) + '/' + filename

        client = boto3.client('s3', **self.credentials)
        with open(dst, 'wb') as data:
            client.download_fileobj(
                Bucket=self.bucket_name,
                Key=src,
                Fileobj=data
            )

        return dst

    def clear_variants(self):
        """
        Clear variants
        Iterates through storage and removes all files that are not originals.
        This is a good way to clear residual files not being used and
        regenerate the once in use.

        Please, also consider configure bucket lifecycle expiration policy
        in order to removed older images.
        :return: Bool
        """
        client = boto3.client('s3', **self.credentials)
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket_name)

        delete_us = dict(Objects=[])
        bucket = self.bucket_name
        for item in pages.search('Contents'):
            if not item: continue
            key = str(item['Key'])

            # skip dirs
            if key.endswith('/'):
                continue

            # skip originals
            parts = key.split('/')
            length = len(parts)
            if parts[length-1] == parts[length-2]: continue

            delete_us['Objects'].append(dict(Key=item['Key']))

            # flush full page
            if len(delete_us['Objects']) >= 999:
                client.delete_objects(Bucket=bucket, Delete=delete_us)
                delete_us = dict(Objects=[])

        # flush last page
        if len(delete_us['Objects']):
            client.delete_objects(Bucket=bucket, Delete=delete_us)

        return True