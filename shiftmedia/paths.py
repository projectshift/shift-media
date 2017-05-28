import hashlib
from shiftmedia.config.default import DefaultConfig
from shiftmedia import exceptions as x
from shiftmedia import utils


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
            output_format=None,
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

        # guess format from original if not specified
        if not output_format:
            parts = id.split('-')
            output_format= parts[5][parts[5].index('.') + 1:]

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
        unsigend_filename = schema.format(**params)

        # sign
        params['sig'] = self.generate_signature(id, unsigend_filename)
        signed_filename = signed_schema.format(**params)
        return signed_filename

    def get_manual_crop_filename(
        self,
        id,
        sample_size,
        target_size,
        output_format=None,
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

        # guess format from original if not specified
        if not output_format:
            parts = id.split('-')
            output_format= parts[5][parts[5].index('.') + 1:]

        # prepare upscale
        upscale = 'upscale' if bool(upscale) else 'noupscale'

        # initial filename
        schema = '{target}-{sample}-{quality}-{upscale}.{format}'
        signed_schema = '{target}-{sample}-{quality}-{upscale}-{sig}.{format}'
        params = dict(
            sample=sample_size,
            target=target_size,
            quality=quality,
            upscale=upscale,
            format=output_format
        )
        unsigend_filename = schema.format(**params)

        # sign
        params['sig'] = self.generate_signature(id, unsigend_filename)
        signed_filename = signed_schema.format(**params)
        return signed_filename

    def filename_to_resize_params(self, id, filename):
        """
        Filename to parameters
        Parses resize filename to a set of usable parameters. Will perform
        filename signature checking and throw an exception if requested
        resize filename is malformed.

        :param id: string - unique storage id
        :param filename: string - resize filename
        :return: dict of parameters
        """

        # validate signature
        if not self.validate_signature(id, filename):
            err = 'Unable to parse filename: bad signature'
            raise x.InvalidArgumentException(err)

        # get parts
        parts = filename.split('-')
        target_size,sample_size,quality,upscale,rest = parts
        target_format = rest[rest.index('.') + 1:]

        # detect manual/auto
        if sample_size in ['fill', 'fit']:
            resize = 'auto'
        else:
            err = False
            sample_size = sample_size.split('x')
            for dimension in sample_size:
                if not dimension.isdigit() or int(dimension) <= 0:
                    err = True
                    break
            if err or len(sample_size) != 2:
                err = 'Unable to parse filename: bad sample size or crop factor'
                raise x.InvalidArgumentException(err)
            else:
                resize = 'manual'

        # validate size
        err = False
        target_size = target_size.split('x')
        for dimension in target_size:
            if not dimension.isdigit() or int(dimension) <= 0:
                err = True
                break
        if err or len(target_size) != 2:
            err = 'Unable to parse filename: bad target size'
            raise x.InvalidArgumentException(err)

        # validate quality
        if not str(quality).isdigit():
            err = 'Quality must be numeric'
            raise x.InvalidArgumentException(err)

        # prepare upscale
        upscale = True if upscale == 'upscale' else False

        # prepare result
        result = dict(
            id=id,
            resize_mode=resize,
            target_size='x'.join(target_size),
            output_format=target_format,
            quality=int(quality),
            filename=filename,
            upscale=upscale
        )

        if resize == 'auto':
            result['factor'] = sample_size
        if resize == 'manual':
            result['sample_size'] = 'x'.join(sample_size)

        return result


