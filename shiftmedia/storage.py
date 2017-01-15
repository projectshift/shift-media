import os
from pathlib import Path
import uuid
from shiftmedia import exceptions as x
from shiftmedia.resizer import Resizer
from shiftmedia import utils


class Storage:

    def __init__(self, config, backend):
        self.config = config
        self.backend = backend
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

    def generate_id(self, original_format):
        """
        Generate id
        Accepts an original file type and generates id string.
        Id will look like this:
            3c72aedc-ba25-11e6-a569-406c8f413974-jpg

        :param original_format: original file type
        :return: storage id
        """
        extension = utils.normalize_extension(original_format)
        id = str(uuid.uuid1()) + '-' + extension
        return id

    def put(self, src, filename=None, delete_local=True):
        """
        Put local file to storage
        Generates a uuid for the file, tells backend to accept
        it by that id and removes original on success.
        """

        # todo: validate file before put
        # todo: get real file extension to generate id with
        # todo: were should this validation happen?

        if not os.path.exists(src):
            msg = 'Unable to find local file [{}]'
            raise x.LocalFileNotFound(msg.format(src))

        extension = ''.join(Path(src).suffixes)
        if not filename:
            filename = 'original.' + extension

        id = self.generate_id(extension)
        self.backend.put(src, id, filename)
        if delete_local:
            os.remove(src)
        return id

    def delete(self, id):
        """
        Delete
        Removes file and all its artifacts from storage by id
        """
        return self.backend.delete(id)

    def filename_to_resize_params(self, filename):
        """
        Filename to parameters
        Parses resize filename to a set of usable parameters. Will perform
        filename signature checking and throw an exception if requested
        resize filename is malformed.

        :param filename: resize filename
        :return: dict of parameters
        """

        """
        (1) AUTOCROP FORMAT:
            * schema id (1)
            * id (3c72aedc-ba25-11e6-a569-406c8f413974-jpg)
            * size (200x300)
            * fit/fill (fill)
            * format (jpg)
            * quality (100)
            * upscale (scale)<-- move to settings?
            * signature (12345)

        (2) MANUAL CROP FORMAT:
            * schema id (2)
            * id (3c72aedc-ba25-11e6-a569-406c8f413974-jpg)
            * size
            * box selection (must be proportional to size)
            * format
            * quality
            * upscale <-- move to settings?
            * signature

        """

        #todo: is id=path, or is it backend logic
        #todo: put original vs put resize
        #todo: problem with backend is that it only puts originals
        #todo: to solve this we need filename schema
        #todo: why does it require id separately? - because how to organize it is up to storage

        #todo: filename MUST include path
        #todo: put methods return full backend paths to file
        #todo: every backend method should accept src, path and filename

        original_schema1 = 'jpg-3c72aedc-ba25-11e6-a569-406c8f413974'
        original_schema2 = '3c72aedc-ba25-11e6-a569-406c8f413974-jpg'

        resize_schema1 = '3c72aedc/ba25/11e6-a569/406c8f413974/200x300-fit-100-upscale-SIGNME.jpg'
        resize_schema2 = '3c72aedc-ba25-11e6-a569-406c8f413974-200x300-0x0-20x30-jpg-100-upscale'

        # todo: if this is the result of put, then why is it backend handled
        # todo: we do not actually need that. result of put must be an id
        # todo: this will get used only by link-builder and resize parser
        # todo: backend can decide how to store stuff based on id



        # USE CASE:
        #       1. UPLOAD ORIGINAL
        #          Original gets assigned an id and put to storage

        #       2. GET SOMETHING BACK
        #          What is this something? An id?

        #       3. USE THAT TO GET ORIGINAL
        #          No extra storage queries to get extension
        #          It must contain extension in the id

        #       3. USE THAT TO CREATE RESIZE 





        print('FILENAME:', filename)


    def create_resize(self):
        """
        Create resize
        Retrieve resize from storage to local temp.
        Perform resize and put back to storage.
        Return url of resized image.
        """
        id_format = ''
