from PIL import Image
from math import floor


class Resizer:

    # resize modes (crop factor)
    RESIZE_TO_FILL = 'mode_resize_to_fill'
    RESIZE_TO_FIT = 'mode_resize_to_fit'

    # rezise to fill algorithms
    RESIZE_SAMPLE = 'algo_resize_sample'
    RESIZE_ORIGINAL = 'algo_resize_original'

    @staticmethod
    def get_ratio(src, dst, mode=None, algo=None, upscale=False):
        """
        Get ratio
        Calculates resize ratio and crop offset for two resize modes:
            * Resize to fit original
            * Resize to fill target

        May additionally perform source image upscale in case it is smaller
        than requested target size.

        """
        if not mode: mode = Resizer.RESIZE_TO_FILL
        if not algo: algo = Resizer.RESIZE_SAMPLE

        if mode == Resizer.RESIZE_TO_FIT:
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
        Resizes original to fit target size without discarding anything.
        In this mode most of the time resulting size will be smaller
        than requested.
        """
        new_size = {0: 0, 1: 0}

        # both sides smaller
        if src[0] <= dst[0] and src[1] <= dst[1]:
            if not upscale:
                # no upscale: return src
                return (src[0], src[1]), (0, 0)
            else:
                # upscale - fit closest side
                percents = [dst[0] / (src[0] / 100), dst[1] / (src[1] / 100)]
                percents = [p if p < 100 else p * -1 for p in percents]
                closest_side = 0 if percents[0] >= percents[1] else 1
                other_side = 1 if closest_side == 0 else 0
                ratio = src[closest_side] / dst[closest_side]
                new_size[closest_side] = dst[closest_side]
                new_size[other_side] = floor(src[other_side] / ratio)
                return (new_size[0], new_size[1]), (0, 0)

        # one side smaller - fit the other
        elif src[0] <= dst[0] or src[1] <= dst[1]:
            short_side = 0 if src[0] <= dst[0] else 1
            other_side = 1 if short_side == 0 else 0
            ratio = src[other_side] / dst[other_side]
            new_size[other_side] = dst[other_side]
            new_size[short_side] = floor(src[short_side] / ratio)
            return (new_size[0], new_size[1]), (0, 0)

        # src bigger - fit longer side
        else:
            longer_side = 0 if src[0] >= src[1] else 1
            other_side = 0 if longer_side == 1 else 1
            ratio = src[longer_side] / dst[longer_side]
            new_size[longer_side] = dst[longer_side]
            new_size[other_side] = floor(src[other_side] / ratio)
            return (new_size[0], new_size[1]), (0, 0)



    @staticmethod
    def get_ratio_to_fill(src, dst, algo, upscale=False):
        """
        Get ratio to fit
        Eesizes original to fill destination and discards excess.
        In this mode most of the time original will be cropped.

        Operates in two modes:
            resize_original - shrinks src to fit dst, then cuts excess
            resize_sample - enlarges dst to fit src, then shrinks

        The second algorithm might be more performant as we  resize
        smaller sample, not the full original.
        """
        new_size = {0: 0, 1: 0}
        offset = {0: 0, 1: 0}

        # no upscale
        if not upscale:

            # both sides smaller - return src
            if src[0] <= dst[0] and src[1] <= dst[1]:
                return (src[0], src[1]), (0, 0)

            # one side smaller - crop the other
            elif src[0] <= dst[0] or src[1] <= dst[1]:
                short_side = 0 if src[0] <= dst[0] else 1
                other_side = 1 if short_side == 0 else 1
                new_size[short_side] = src[short_side]
                new_size[other_side] = dst[other_side]
                offset[short_side] = 0
                offset[other_side] = floor(
                    (dst[other_side] - src[other_side]) / 2
                )
                return (new_size[0], new_size[1]), (offset[0], offset[1])


            # src bigger - fit closest
            else:
                pass


        # upscale
            # one side smaller - enlarge until it fits
            # both sides smaller - enlarge until closest fits
            # normal - enlarge closest



        #todo both sides are shorter and upscale
        return 'bull', 'shit'




        # if one src side is shorter than same dst side, crop the other
        if src[0] <= dst[0] or src[1] <= dst[1] and not upscale:


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





