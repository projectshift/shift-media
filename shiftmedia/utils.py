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


def generate_id(original_filename):
    """
    Generate id
    Accepts an original filename and generates id string.
    Id will look like this:
        3c72aedc-ba25-11e6-a569-406c8f413974-original_filename.jpg

    :param original_filename: string - original file name
    :return: string - storage id
    """

    # todo: how to make filename part of id?
    # todo: whatever is our separator, it can not be part of filename
    # todo: 3c72aedc-ba25-11e6-a569-406c8f413974-original-filename.jpg
    # todo: however uuid consists of exactly 5 sequences

    id = str(uuid.uuid1()) + '-' + original_filename.lower()
    return id