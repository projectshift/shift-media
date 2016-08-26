import uuid


class Item:
    """
    Media item
    This represent an actual media item wether an image, video or downloadable.
    Upon instantiation it will get a unique UUID for identification.
    """

    def __init__(self):
        """ initialize the item """
        self.id = uuid.uuid1()
        self.src = None




