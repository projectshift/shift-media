from PIL import Image
import pdb


class Resizer:



    @staticmethod
    def resize(src, dst, size, crop='inset', position=None):
        """
        Resize
        Creates resize from the given parameters
        Crop outbound: resize to fill
        Crop inset: resize to fit (thumbnail)
        """

        # todo: create resize definition schema
        # todo: do we enlarge if original smaller than dest

        # get sizes
        size = size.split('x')
        dst_width = int(size[0])
        dst_height = int(size[1])

        img = Image.open(src)
        src_width = img.size[0]
        src_height = img.size[1]

        # is src smaller than dst?
        upscale = src_width < dst_width or src_height < dst_height

        print(img.size, upscale)


