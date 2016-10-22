from PIL import Image
from math import floor


class Resizer:

    @staticmethod
    def getRatio(src, dst):
        """
        Get ratio
        Calculates resize ratio based on source and destination size
        """
        percents = (dst[0] / (src[0] / 100), dst[1] / (src[1] / 100))
        closest_side = 0 if percents[0] >= percents[1] else 1
        other_side = int(not bool(closest_side))
        ratio = src[closest_side] / dst[closest_side]

        new_size = dict()
        new_size[closest_side] = dst[closest_side]
        new_size[other_side] = floor(src[other_side] / ratio)

        # todo: now figure top-left position
        center_by = other_side
        crop_position = dict()
        crop_position[closest_side] = 0
        crop_position[center_by] = round(
            (new_size[center_by] - dst[center_by]) / 2
        )

        return (new_size[0], new_size[1]), (crop_position[0], crop_position[1])



    @staticmethod
    def resize(src, dst, size, crop='inset', position=None):
        """
        Resize
        Creates resize from the given parameters
        Crop outbound: resize to fill
        Crop inset: resize to fit (thumbnail)
        """

        # get sizes
        dst_size = [int(x) for x in size.split('x')]
        dst_width = dst_size[0]
        dst_height = dst_size[1]


        # image = Image.open(src) # wi don't even need pil here we can use maths
        # src_size = image.size

        image_sizes = dict(h=(5000, 2000), v=(2000, 5000), s=(3000, 3000))
        src_size = image_sizes['h']
        src_width = src_size[0]
        src_height = src_size[1]

        # is src smaller than dst?
        upscale = src_width < dst_width or src_height < dst_height

        # for now
        assert not upscale

        # get ratio
        short_side = 0 if min(src_size) == src_width else 1
        ratio = src_size[short_side] / dst_size[short_side]

        # todo: which src side will intersect dst first if proportionally resized
        #

        print('RATIO:', ratio)

        # get new size
        dst_width = floor(src_width / ratio)
        dst_heigh = floor(src_height / ratio)

        print('SRC: ', src_size)
        print('DST: ', (dst_width, dst_heigh))

        # print(src_size, dst_width, dst_heigh)


