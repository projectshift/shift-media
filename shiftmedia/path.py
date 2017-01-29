
class PathBuilder:
    """
    Path Builder
    Converts resize filepaths to a set of resize parameters. Also converts
    resize parameters to storage filepaths. Used to build links and create
    resizes.
    """

    def validate_signature(self, id, filename):
        """
        Validate signature
        Accepts storage id and a filename and validates hash signature.
        Signatures are used to prevent brute force attack against
        resizing service.

        :param id:
        :param filename:
        :return:
        """
        pass

    def generate_signature(self, id, filename):
        """
        Generate signature
        Accepts storage id and a filename to generate hash signature.
        Signatures are used to prevent brute force attack against
        resizing service.

        :param id:
        :param filename:
        :return:
        """
        pass



    def get_autocrop_url(self, id, size, factor, output_format, upscale=True):
        """
        Get autocrop url
        Encodes parameters for automatic cropping/resizing into a filename.

        :param id:
        :param size:
        :param factor:
        :param output_format:
        :param upscale:
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