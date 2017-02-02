import hashlib
from shiftmedia.config.default import DefaultConfig
from shiftmedia import exceptions as x


# todo: paths will need secret_key to sign/validate url
# todo: secret_key comes from config, but we may request it in constructor
# todo: what would be the easiest way to use this from client code?
# todo: we can pass the secret all around and then wrap these methods
# todo: or we can require mandatory instantiation
# todo: passing secret around seems better although pollutes method signatures
# todo: it will also be hard to use link builder standalone
# todo: link builder has a dependency (config) and thus is a service

# todo: THINK OF A BETTER NAME


class PathBuilder:

    def __init__(self, secret_key):
        """
        Path builder constructor
        Initializes path builder service
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
        :param secret_key: - string, secret key to use as salt
        :return: string - signature
        """
        sign_me = bytes(id + filename + self.secret_key, 'utf-8')
        signature = hashlib.md5()
        signature.update(sign_me)
        return signature.hexdigest()

    def validate_signature(self, id, filename, secret_key):
        """
        Validate signature
        Accepts storage id and a filename and validates hash signature.
        Signatures are used to prevent brute force attack against
        resizing service.

        :param id: string - storage id
        :param filename: - string, resize filename
        :param secret_key: - string, secret key to use as salt
        :return:
        """
        pass

    def get_autocrop_filename(
            self,
            id,
            size,
            factor,
            output_format,
            upscale=True,
            quality=65
        ):
        """
        Get autocrop filename
        Encodes parameters for automatic cropping/resizing into a filename.

        :param id: string - storage id
        :param size: string - width x height
        :param factor: string - crop factor, fit/fill
        :param output_format: string - output format
        :param upscale: bool - enlarge smaller original
        :param upscale: bool - enlarge smaller original
        :return:
        """
        pass


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