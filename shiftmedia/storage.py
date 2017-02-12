import os
from pathlib import Path

from shiftmedia import utils, exceptions as x
from shiftmedia.paths import PathBuilder
from shiftmedia.resizer import Resizer


class Storage:

    def __init__(self, config, backend):
        self.config = config
        self.backend = backend
        self.paths = PathBuilder(config.SECRET_KEY)
        self._tmp_path = config.LOCAL_TEMP

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

        # TODO: Implement file validation

        if not os.path.exists(src):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(src))

        path = Path(src)
        extension = ''.join(path.suffixes)[1:]
        name = path.name.replace('.' + extension, '')
        extension = utils.normalize_extension(extension)
        filename = name + '.' + extension
        id = utils.generate_id(filename)
        self.backend.put(src, id)
        if delete_local: os.remove(src)
        return id

    def delete(self, id):
        """
        Delete
        Removes file and all its artifacts from storage by id
        """
        return self.backend.delete(id)

    def create_resize(self, url):
        """
        Create resize
        Accepts storage URL of a resize, parses and validates it and then
        creates the resize to be put back to storage.

        :param url: string - url of resize to be created
        :return: string - same url on success
        """
        # todo: test me
        id, filename = self.backend.parse_resize_url(url)
        resize_params = self.paths.filename_to_resize_params(id, filename)
        local_original = self.backend.retrieve_original(id, self._tmp_path)
        resize = Resizer.resize(**resize_params)
        self.backend.put(resize, id, filename)
        os.remove(local_original)
        os.remove(resize)
        return url




