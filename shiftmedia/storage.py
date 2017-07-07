import os
from pathlib import Path

from shiftmedia import utils, exceptions as x
from shiftmedia.paths import PathBuilder
from shiftmedia.resizer import Resizer


class Storage:
    def __init__(self, backend, secret_key, local_temp):
        """
        Init
        :param backend:, shiftmedia.backend.Backend instance
        :param secret_key: string, random salt
        :param local_temp: string, path to local temp directory
        """
        self.backend = backend
        self.paths = PathBuilder(secret_key)
        self._tmp_path = local_temp

    @property
    def tmp(self):
        """
        Get temp path
        Returns path to local temp and creates one if necessary
        """
        if not os.path.exists(self._tmp_path):
            os.makedirs(self._tmp_path)
        return self._tmp_path

    def put(self, src, delete_local=True):
        """
        Put local file to storage
        Generates a uuid for the file, tells backend to accept
        it by that id and removes original on success.
        """

        # TODO: Implement file validation (libmagic)

        if not os.path.exists(src):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(src))

        path = Path(src)
        extension = ''.join(path.suffixes)[1:]
        name = path.name.replace('.' + extension, '')
        extension = utils.normalize_extension(extension)
        filename = name + '.' + extension
        id = utils.generate_id(filename)
        self.backend.put_variant(src, id, filename)
        if delete_local: os.remove(src)
        return id

    def delete(self, id):
        """
        Delete
        Removes file and all its artifacts from storage by id
        """
        return self.backend.delete(id)

    def get_original_url(self, id):
        """
        Get original URL
        Combines backend base url, path to object id and original filename.
        :return: string - full object url
        """
        base = self.backend.get_url().strip('/')
        parts = self.backend.id_to_path(id)
        filename = parts[5]
        path = '/'.join(parts)
        return base + '/' + path + '/' + filename

    def get_auto_crop_url(self, *args, **kwargs):
        """
        Get auto crop URL
        Combines backend base url, path to object id and generated filename.
        :param args: positional args to be passed to filename generator
        :param kwargs: keyword args to be passed to filename generator
        :return: string - full object url
        """
        id = kwargs['id'] if 'id' in kwargs else args[0]
        base = self.backend.get_url().strip('/')
        parts = self.backend.id_to_path(id)
        path = '/'.join(parts)
        filename = self.paths.get_auto_crop_filename(*args, **kwargs)
        return base + '/' + path + '/' + filename

    def get_manual_crop_url(self, *args, **kwargs):
        """
        Get manual crop URL
        Combines backend base url, path to object id and generated filename.
        :param args: positional args to be passed to filename generator
        :param kwargs: keyword args to be passed to filename generator
        :return: string - full object url
        """
        id = kwargs['id'] if 'id' in kwargs else args[0]
        base = self.backend.get_url().strip('/')
        parts = self.backend.id_to_path(id)
        path = '/'.join(parts)
        filename = self.paths.get_manual_crop_filename(*args, **kwargs)
        return base + '/' + path + '/' + filename

    def create_resize(self, url):
        """
        Create resize
        Accepts storage URL of a resize, parses and validates it and then
        creates the resize to be put back to storage.
        :param url: string - url of resize to be created
        :return: string - same url on success
        """
        id, filename = self.backend.parse_url(url)
        params = self.paths.filename_to_resize_params(id, filename)
        mode = params['resize_mode']
        modes = ['auto', 'manual']
        if mode not in modes:
            err = 'Resize mode [' + mode + '] is not yet implemented.'
            raise x.NotImplementedError(err)

        local_original = self.backend.retrieve_original(id, self._tmp_path)
        local_resize = os.path.join(self._tmp_path, id, params['filename'])
        factor = Resizer.RESIZE_TO_FIT
        if params['factor'] == 'fill':
            factor = Resizer.RESIZE_TO_FILL

        resize = Resizer.auto_crop(
            src=local_original,
            dst=local_resize,
            size=params['target_size'],
            mode= factor,
            upscale=params['upscale'],
            format=params['output_format'],
            quality=params['quality']
        )

        try:
            self.backend.put_variant(resize, id, filename, force=True)
        except x.FileExists:
            pass

        os.remove(local_original)
        os.remove(resize)
        tmp_dir = os.path.join(self._tmp_path, id)
        if not os.listdir(tmp_dir):
            os.rmdir(tmp_dir)
        return url




