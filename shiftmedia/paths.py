import hashlib
from shiftmedia.config.default import DefaultConfig
from shiftmedia import exceptions as x


class PathBuilder:

    def __init__(self, secret_key):
        """
        Path builder constructor
        Initializes path builder service.
        :param secret_key: string - secret key from config
        """
        self.validate_secret_key(secret_key)
        self.secret_key = secret_key

    def validate_secret_key(self, secret_key):
        """
        Validate secret key
        Makes sure secret key is not equal to default. Prevents security
        vulnerability when using default one.

        :param secret_key: string, secret key to validate
        :return: bool
        """
        if secret_key == DefaultConfig.SECRET_KEY:
            msg = 'Security warning: using default secret key '
            raise x.ConfigurationException(msg)

        return True

    def generate_signature(self, id, filename):
        """
        Generate signature
        Accepts storage id and a filename to generate hash signature.
        Signatures are used to prevent brute force attack against
        resizing service.

        :param id: string - storage id
        :param filename: - string, resize filename
        :return: string - signature
        """
        sign_me = bytes(id + filename + self.secret_key, 'utf-8')
        signature = hashlib.md5()
        signature.update(sign_me)
        return signature.hexdigest()

    def validate_signature(self, id, filename):
        """
        Validate signature
        Accepts storage id and a filename and validates hash signature.
        Signatures are used to prevent brute force attack against
        resizing service.

        :param id: string - storage id
        :param filename: - string, resize filename
        :return:
        """

        parts = filename.split('-')
        extension = parts[4][parts[4].index('.'):]
        non_signed_filename = '-'.join(parts[:4]) + extension
        signature = parts[4].replace(extension, '')
        return signature == self.generate_signature(id, non_signed_filename)


    def get_auto_crop_filename(
            self,
            id,
            size,
            factor,
            output_format='jpg',
            upscale=True,
            quality=65
    ):
        """
        Get auto crop filename
        Encodes parameters for automatic cropping/resizing into a filename.
        Resulting filename will contain hash signature.

        :param id: string - storage id (used to generate signature)
        :param size: string - width x height
        :param factor: string - crop factor, fit/fill
        :param output_format: string - output format
        :param upscale: bool - enlarge smaller original
        :param quality: string - differs per format. i.e. 0-100 for jpg
        :return: string - signed filename
        """

        # validate size
        err = False
        dimensions = size.lower().split('x')
        if len(dimensions) != 2:
            err = True
        for dimension in dimensions:
            if not dimension.isdigit() or int(dimension) <= 0:
                err = True
        if err:
            err = 'Invalid size provided must be in 100x200 format'
            raise x.InvalidArgumentException(err)

        # validate factor
        if factor not in ['fit', 'fill']:
            err = 'Auto crop factor must be either fit or fill'
            raise x.InvalidArgumentException(err)

        # validate quality
        if not str(quality).isdigit():
            err = 'Quality must be numeric'
            raise x.InvalidArgumentException(err)

        # prepare upscale
        upscale = 'upscale' if bool(upscale) else 'noupscale'

        # create filename filename
        schema = '{size}-{factor}-{quality}-{upscale}.{format}'
        signed_schema = '{size}-{factor}-{quality}-{upscale}-{sig}.{format}'
        params = dict(
            size=size,
            factor=factor,
            quality=quality,
            upscale=upscale,
            format=output_format
        )
        nonsigend_filename = schema.format(**params)

        # sign
        params['sig'] = self.generate_signature(id, nonsigend_filename)
        signed_filename = signed_schema.format(**params)
        return signed_filename

    def get_manual_crop_filename(
            self,
            id,
            sample_size,
            target_size,
            output_format='jpg',
            upscale=True,
            quality=65
    ):
        """
        Get manual crop filename
        Encodes parameters for automatic cropping/resizing into a filename.
        Resulting filename will contain hash signature.

        :param id: string - storage id (used to generate signature)
        :param target_size: string - width x height
        :param sample_size: string - width x height, must be proportional
        :param output_format: string - output format
        :param upscale: bool - enlarge smaller original
        :param quality: string - differs per format. i.e. 0-100 for jpg
        :return: string - signed filename
        """

        # validate sample size
        err = False
        sample_dimensions = sample_size.lower().split('x')
        if len(sample_dimensions) != 2:
            err = True
        for dimension in sample_dimensions:
            if not dimension.isdigit() or int(dimension) <= 0:
                err = True
        if err:
            err = 'Invalid sample size provided must be in 100x200 format'
            raise x.InvalidArgumentException(err)

        # validate target size
        err = False
        target_dimensions = target_size.lower().split('x')
        if len(target_dimensions) != 2:
            err = True
        for dimension in target_dimensions:
            if not dimension.isdigit() or int(dimension) <= 0:
                err = True
        if err:
            err = 'Invalid target size provided must be in 100x200 format'
            raise x.InvalidArgumentException(err)

        # validate sample and target sizes being proportional
        sw = int(sample_dimensions[0])
        sh = int(sample_dimensions[1])
        tw = int(target_dimensions[0])
        th = int(target_dimensions[1])
        if (sw/sh) != (tw/th):
            err = 'Sample size and target size must be proportional'
            raise x.InvalidArgumentException(err)

        # validate quality
        if not str(quality).isdigit():
            err = 'Quality must be numeric'
            raise x.InvalidArgumentException(err)

        # prepare upscale
        upscale = 'upscale' if bool(upscale) else 'noupscale'

        # initial filename
        schema = '{sample}-{target}-{quality}-{upscale}.{format}'
        signed_schema = '{sample}-{target}-{quality}-{upscale}-{sig}.{format}'
        params = dict(
            sample=sample_size,
            target=target_size,
            quality=quality,
            upscale=upscale,
            format=output_format
        )
        nonsigend_filename = schema.format(**params)

        # sign
        params['sig'] = self.generate_signature(id, nonsigend_filename)
        signed_filename = signed_schema.format(**params)
        return signed_filename





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

        id = '3c72aedc-ba25-11e6-a569-406c8f413974-jpg'
        resize_schema1 = '3c72aedc/ba25/11e6-a569/406c8f413974/200x300-fit-100-upscale-SIGNME.jpg'
        resize_schema2 = '3c72aedc-ba25-11e6-a569-406c8f413974-200x300-0x0-20x30-jpg-100-upscale'

        print('FILENAME:', filename)