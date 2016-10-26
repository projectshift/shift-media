from PIL import Image
from math import floor


class Resizer:

    # resize modes (crop factor)
    CROP_TO_FILL = 'mode_crop_to_fill'
    CROP_TO_FIT = 'mode_crop_to_fit'

    # rezise to fill algorithms
    RESIZE_SAMPLE = 'algo_resize_sample'
    RESIZE_ORIGINAL = 'algo_resize_original'

    @staticmethod
    def get_ratio(src, dst, mode=None, algo=None, upscale=False):
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
        if not mode: mode = Resizer.CROP_TO_FILL
        if not algo: algo = Resizer.RESIZE_SAMPLE

        # if src smaller than original and no upscale - return src
        if src[0] <= dst[0] and src[1] <= dst[1] and not upscale:
            return dict(size=(src[0], src[1]), position=(0, 0))

        if mode == Resizer.CROP_TO_FIT:
            result = Resizer.get_ratio_to_fit(src, dst, upscale)
        else:
            result = Resizer.get_ratio_to_fill(src, dst, algo, upscale)

        # return result
        return dict(
            size=result[0],
            position=result[1],
        )


    @staticmethod
    def get_ratio_to_fit(src, dst, upscale=False):
        """
        Get ratio to fit
        Proportionally resizes original to fit target size without discarding
        anything. Most of the time resulting size will be smaller than
        requested target size, unless both original and target sizes have the
        same proportions.
        """

        # if one src side shorter than dst, make the other one fit
        if src[0] <= dst[0] or src[1] <= dst[1] and not upscale:
            short_side = 0 if src[0] <= dst[0] else 1
            other_side = 1 if short_side == 0 else 1

            ratio = src[other_side] / dst[other_side]
            new_size = dict()
            new_size[other_side] = dst[other_side]
            new_size[short_side] = floor(src[short_side] / ratio)
            return (new_size[0], new_size[1]), (0,0)

        # otherwise resize to fit normally
        longer_side = 0 if src[0] >= src[1] else 1
        other_side = 0 if longer_side == 1 else 1
        ratio = src[longer_side] / dst[longer_side]

        new_size = dict()
        new_size[longer_side] = dst[longer_side]
        new_size[other_side] = floor(src[other_side] / ratio)
        return (new_size[0], new_size[1]), (0,0)

    def get_ratio_to_fill(self, src, dst, algo, upscale=False):
        """
        Get ratio to fit
        Proportionally resizes original to fill destination and discards excess.
        May optionally upscale original if it's smaller than target size.

        Operates in two modes:
            resize_original - shrinks src to fit dst, then cuts excess
            resize_sample - enlarges dst to fit src, then shrinks

        The second algorithm might be more performant as we  resize
        smaller sample, not the full original.
        """

        # if one src side is shorter than same dst side, crop the other
        if src[0] <= dst[0] or src[1] <= dst[1] and not upscale:
            short_side = 0 if src[0] <= dst[0] else 1
            other_side = 1 if short_side == 0 else 1

            new_size = dict()
            new_size[short_side] = src[short_side]
            new_size[other_side] = dst[other_side]

            offset = dict()
            offset[other_side] = 0
            offset[short_side] = floor(
                (dst[other_side] - src[other_side]) / 2
            )

            return (new_size[0], new_size[1]), (offset[0], offset[1])

        # otherwise resize to fill normally
        percents = (dst[0] / (src[0] / 100), dst[1] / (src[1] / 100))
        closest_side = 0 if percents[0] >= percents[1] else 1
        other_side = 1 if closest_side == 0 else 0
        ratio = src[closest_side] / dst[closest_side]

        # get new size and crop offset to center
        new_size = dict()
        new_size[closest_side] = 0
        new_size[other_side] = 0

        offset = dict()
        offset[closest_side] = 0
        offset[other_side] = 0

        # enlarge dst
        # todo: test if this one is quicker
        # todo: this will not work with upscaling
        if algo == Resizer.RESIZE_SAMPLE:
            new_size[closest_side] = src[closest_side]
            new_size[other_side] = floor(dst[other_side] * ratio)
            offset[other_side] = round(
                (src[other_side] - dst[other_side]) / 2
            )

        # shrink src
        # todo: test if this one is quicker
        if algo == Resizer.RESIZE_ORIGINAL:
            new_size[closest_side] = dst[closest_side]  # shrink src
            new_size[other_side] = floor(dst[other_side] * ratio)
            offset[other_side] = round(
                (src[other_side] - dst[other_side]) / 2
            )

        # and return
        return (new_size[0], new_size[1]), (offset[0], offset[1])





