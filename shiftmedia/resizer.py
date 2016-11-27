from PIL import Image, ImageSequence
from math import floor


class Resizer:
    """
    Resizer
    Handles resizing of local image files using different crop-factors.
    Supports resizing to fill or to fit with optional upscale for static
    images and animated GIFs.

    A note on algorithms
    When producing resize from large original we can make it in two ways:

        - Scale down original and discard excess
        - Take a proportional sample of original and scale sample down

    The former performs scaling on a larger image, when the latter only
    operates with a sample area in question, wich is always smaller.

    In reality performance testing shows very little difference:

        - Resize original:  158.1552695589926 seconds
        - Resize sample:    136.1955325910094 seconds

    Testing was done on a 1GB directory of 1551 JPEG images. Although the
    difference is negligible we might still prefer faster approach.
    """

    # resize modes (crop factor)
    RESIZE_TO_FILL = 'mode_resize_to_fill'
    RESIZE_TO_FIT = 'mode_resize_to_fit'

    @staticmethod
    def resize(
            src,
            dst,
            size,
            mode=None,
            upscale=False,
            format=None,
            quality=100
    ):
        """
        Resize and write
        Accepts source and destination path, as well as target size
        and format. May optionally perform upscale in case src image is
        smaller than target size. Writes file to destination on success.

        A note on GIFs:
        As there is currently an issue ('unknown raw mode') in Pillow when
        working with GIFs that are in mode=P, we have to forcefully convert
        image mode to RGBA for gif images to preserve animation.

        :param src: Source file path
        :param dst: Destination file path
        :param size: Target size
        :param mode: Resize mode (fit/fill)
        :param upscale: Whether to enlarge src if its smaller than dst
        :param format: Target format (None to guess by extension)
        :param quality: Output quality
        :return: destination image path
        """
        img = Image.open(src)
        animated_gif = 'duration' in img.info and img.info['duration'] > 0

        # resize regular image
        if not animated_gif:
            img = img.convert(mode='RGBA')
            img = Resizer.resize_img(img, size, mode, upscale)
            img.save(dst, format=format)

        # resize animated gif
        else:
            out = img.convert(mode='RGBA')
            out = Resizer.resize_img(out, size, mode, upscale)
            frames = []
            for index, frame in enumerate(ImageSequence.Iterator(img)):
                if index == 0: continue
                frame = frame.convert(mode='RGBA')
                frame = Resizer.resize_img(frame, size, mode, upscale)
                frames.append(frame)
            out.save(dst, format=format, save_all=True, append_images=frames)

        # and return
        return dst

    @staticmethod
    def resize_img(img, size, mode=None, upscale=False):
        """
        Resize and img return
        Accepts source image (file or object) and target size. May optionally
        perform source image upscale in case it is smaller than dst.
        Does not write anything, but instead returns PIL.Image object which
        makes it reusable for gif sequence animations.

        :param img: Source file path or PIL.Image object
        :param size: Target size
        :param mode: Resize mode (fit/fill)
        :param upscale: Whether to enlarge src if its smaller than dst
        :param write: Write to dst or return image object (for testing)
        :return: PIL.Image object
        """
        mode = mode or Resizer.RESIZE_TO_FILL

        # get size and offset
        img = img if isinstance(img, Image.Image) else Image.open(img)
        src = img.size
        dst = [int(x) for x in size.split('x')]
        ratio = Resizer.get_ratio(src, dst, mode, upscale)
        width, height = ratio['size']
        x, y = ratio['position']

        # get resize logic
        if src[0] <= dst[0] and src[1] <= dst[1]:
            one_side_smaller = original_bigger = False
            original_smaller = True
        elif src[0] <= dst[0] or src[1] <= dst[1]:
            original_smaller = original_bigger = False
            one_side_smaller = True
        else:
            original_smaller = one_side_smaller = False
            original_bigger = True

        # resize to fit, no upscale
        if mode == Resizer.RESIZE_TO_FIT and not upscale:
            if original_smaller:
                pass  # return original
            elif one_side_smaller:
                img = img.resize(ratio['size'], Image.LANCZOS)
            else:
                img = img.resize(ratio['size'], Image.LANCZOS)

        # resize to fit, upscale
        elif mode == Resizer.RESIZE_TO_FIT and upscale:
            if original_smaller:
                img = img.resize(ratio['size'], Image.LANCZOS)
            elif one_side_smaller:
                img = img.resize(ratio['size'], Image.LANCZOS)
            else:
                img = img.resize(ratio['size'], Image.LANCZOS)

        # resize to fill, no upscale
        elif mode == Resizer.RESIZE_TO_FILL and not upscale:
            if original_smaller:
                pass # return original
            elif one_side_smaller:
                box = (x, y, width+x, height+y)
                img = img.crop(box)
            else:
                box = (x, y, width + x, height + y)
                img = img.crop(box)
                img = img.resize(dst, Image.LANCZOS)


        # resize to fill, upscale
        elif mode == Resizer.RESIZE_TO_FILL and upscale:
            if original_smaller:
                box = (x, y, width + x, height + y)
                img = img.crop(box)
                img = img.resize(dst, Image.LANCZOS)

            elif one_side_smaller:
                box = (x, y, width + x, height + y)
                img = img.crop(box)
                img = img.resize(dst, Image.LANCZOS)

            else:
                box = (x, y, width + x, height + y)
                img = img.crop(box)
                img = img.resize(dst, Image.LANCZOS)


        # error out otherwise
        else:
            raise Exception('Invalid resize parameters')

        # and return
        return img


    @staticmethod
    def get_ratio(src, dst, mode, upscale=False):
        """
        Get ratio
        Calculates resize ratio and crop offset for two resize modes:
            * Resize to fit original
            * Resize to fill target

        May additionally perform source image upscale in case it is smaller
        than requested target size.

        """
        if mode == Resizer.RESIZE_TO_FIT:
            result = Resizer.get_ratio_to_fit(src, dst, upscale)
        else:
            result = Resizer.get_ratio_to_fill(src, dst, upscale)

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

        # one side smaller - fit the other side
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
                other_side = 0 if short_side == 1 else 1
                new_size[short_side] = src[short_side]
                new_size[other_side] = dst[other_side]
                offset[short_side] = 0
                offset[other_side] = floor(
                    (src[other_side] - dst[other_side]) / 2
                )
                return (new_size[0], new_size[1]), (offset[0], offset[1])

            # src bigger - fit closest side
            else:
                percents = (dst[0] / (src[0] / 100), dst[1] / (src[1] / 100))
                percents = [p if p < 100 else p * -1 for p in percents]
                closest_side = 0 if percents[0] >= percents[1] else 1
                other_side = 1 if closest_side == 0 else 0
                ratio = src[closest_side] / dst[closest_side]
                new_size[closest_side] = src[closest_side]
                new_size[other_side] = floor(dst[other_side] * ratio)
                offset[other_side] = round(
                    (src[other_side] - new_size[other_side]) / 2
                )
                return (new_size[0], new_size[1]), (offset[0], offset[1])


        # upscale
        if upscale:

            # both sides smaller - enlarge until further fits
            if src[0] <= dst[0] and src[1] <= dst[1]:
                percents = (dst[0] / (src[0] / 100), dst[1] / (src[1] / 100))
                percents = [p if p < 100 else p * -1 for p in percents]
                closest_side = 0 if percents[0] >= percents[1] else 1
                other_side = 1 if closest_side == 0 else 0
                ratio = src[other_side] / dst[other_side]
                new_size[other_side] = src[other_side]
                new_size[closest_side] = floor(dst[closest_side] * ratio)
                offset[closest_side] = round(
                    (src[closest_side] - new_size[closest_side]) / 2
                )

            # one side smaller - enlarge until it fits
            elif src[0] <= dst[0] or src[1] <= dst[1]:
                short_side = 0 if src[0] <= dst[0] else 1
                other_side = 1 if short_side == 0 else 0
                ratio = src[short_side] / dst[short_side]
                new_size[short_side] = src[short_side]
                new_size[other_side] = floor(dst[other_side] * ratio)
                offset[other_side] = round(
                    (src[other_side] - new_size[other_side]) / 2
                )
                return (new_size[0], new_size[1]), (offset[0], offset[1])

            # src bigger - shrink until closest side fits
            else:
                percents = (dst[0] / (src[0] / 100), dst[1] / (src[1] / 100))
                percents = [p if p < 100 else p * -1 for p in percents]
                closest_side = 0 if percents[0] >= percents[1] else 1
                other_side = 1 if closest_side == 0 else 0
                ratio = dst[closest_side] / src[closest_side]
                new_size[closest_side] = src[closest_side]
                new_size[other_side] = floor(dst[other_side] / ratio)
                offset[other_side] = round(
                    (src[other_side] - new_size[other_side]) / 2
                )
                return (new_size[0], new_size[1]), (offset[0], offset[1])
