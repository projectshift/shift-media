import uuid


def normalize_extension(extension):
    """
    Normalize extension
    Converts given extension to canonical format for storage
    :param extension: original extension
    :return: normalized extension
    """
    extension = extension.lower()

    exts = dict()
    exts['jpg'] = ['jpeg','jpe','jif','jfif','jfi''jp2','j2k','jpx','jpf','jpm']
    exts['tif'] = ['tiff']
    exts['tar.gz'] = ['tgz']

    for canonical, variants in exts.items():
        if extension in variants:
            extension = canonical
            break

    return extension


def extension_to_format(extension):
    """
    Extension to image format
    Attempts to convert file extension to image format that Pillow
    library understands.
    :param extension: string - file extension
    :return: string - image format name
    """
    formats = dict()
    formats['jpg'] = 'JPEG'
    formats['tif'] = 'TIFF'

    extension = normalize_extension(extension)
    format = formats[extension] if extension in formats else extension.upper()
    return format


def generate_id(original_filename):
    """
    Generate id
    Accepts an original filename and generates id string.
    Id will look like this:
        3c72aedc-ba25-11e6-a569-406c8f413974-original_filename.jpg

    :param original_filename: string - original file name
    :return: string - storage id
    """
    id = str(uuid.uuid1()) + '-' + original_filename.lower()
    return id