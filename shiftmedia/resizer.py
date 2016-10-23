from PIL import Image
from math import floor


class Resizer:

    @staticmethod
    def getRatio(src, dst, mode='resize_sample'):
        """
        Get ratio
        Calculates resize ratio based on source and destination size.
        For all the calculations assume 0 for width and 1 for height.

        Operates in two modes:
            resize_original - shrinks src to fit dst, then cuts excess
            resize_sample - enlarges dst to fit src, then shrinks

        The second algorithm might be more performant as we  resize
        smaller sample, not the full original.

        """
        percents = (dst[0] / (src[0] / 100), dst[1] / (src[1] / 100))
        closest_side = 0 if percents[0] >= percents[1] else 1
        other_side = 1 if closest_side == 0 else 0
        ratio = src[closest_side] / dst[closest_side]

        # get new size and crop offset to center
        new_size = dict()
        new_size[closest_side] = 0
        new_size[other_side] = 0

        crop_position = dict()
        crop_position[closest_side] = 0
        crop_position[other_side] = 0

        # enlarge dst
        if mode == 'resize_sample':
            new_size[closest_side] = src[closest_side]
            new_size[other_side] = floor(dst[other_side] * ratio)
            crop_position[other_side] = round(
                (src[other_side] - dst[other_side]) / 2
            )

        # shrink src
        if mode == 'resize_original':
            new_size[closest_side] = dst[closest_side] # shrink src
            new_size[other_side] = floor(dst[other_side] * ratio)
            crop_position[other_side] = round(
                (src[other_side] - dst[other_side]) / 2
            )

        # and return
        return dict(
            size =(new_size[0], new_size[1]),
            position=(crop_position[0], crop_position[1])
        )


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

        image = Image.open(src)
        src_size = image.size

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


