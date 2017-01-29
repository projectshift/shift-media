from PIL import Image, ImageSequence
from math import floor


class Resizer:
    """
    Resizer
    Handles resizing of local image files using different crop-factors.
    Supports resizing to fill or to fit with optional upscale for static
    images and animated GIFs.
    """

    # TODO: IMPLEMENT MANUAL RESIZE

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
        if not animated_gif:
            # resize regular image
            img = img.convert(mode='RGBA')
            img = Resizer.resize_img(img, size, mode, upscale)
            img.save(dst, format=format, quality=quality)
        else:
            # resize animated gif
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

        # create image and get size
        img = img if isinstance(img, Image.Image) else Image.open(img)
        src = img.size
        dst = [int(x) for x in size.split('x')]

        # get src sides
        long_side = 0 if src[0] >= src[1] else 1
        short_side = 0 if long_side == 1 else 1

        # get src side shorter than dst (if applicable)
        shorter_side = 0 if src[0] <= dst[0] else 1
        longer_side = 1 if shorter_side == 0 else 0

        # get src side closest to dst
        percents = [dst[0] / (src[0] / 100), dst[1] / (src[1] / 100)]
        percents = [p if p < 100 else p * -1 for p in percents]
        closest_side = 0 if percents[0] >= percents[1] else 1
        farthest_side = 1 if closest_side == 0 else 0

        # get resize logic
        original_smaller = (src[0] <= dst[0] and src[1] <= dst[1])
        original_bigger = (src[0] > dst[0] and src[1] > dst[1])
        one_side_smaller = (src[0] <= dst[0] or src[1] <= dst[1])

        # defaults
        new_size = {0: 0, 1: 0}
        offset = {0: 0, 1: 0}

        # resize to fit
        if mode == Resizer.RESIZE_TO_FIT:
            if original_smaller and not upscale:
                return img
            elif original_smaller and upscale:
                ratio = src[closest_side] / dst[closest_side]
                new_size[closest_side] = dst[closest_side]
                new_size[farthest_side] = floor(src[farthest_side] / ratio)
                resize = (new_size[0], new_size[1])
                return img.resize(resize, Image.LANCZOS)
            elif one_side_smaller:
                ratio = src[longer_side] / dst[longer_side]
                new_size[longer_side] = dst[longer_side]
                new_size[shorter_side] = floor(src[shorter_side] / ratio)
                resize = (new_size[0], new_size[1])
                return img.resize(resize, Image.LANCZOS)
            elif original_bigger:
                ratio = src[long_side] / dst[long_side]
                new_size[long_side] = dst[long_side]
                new_size[short_side] = floor(src[short_side] / ratio)
                resize = (new_size[0], new_size[1])
                return img.resize(resize, Image.LANCZOS)

        # resize to fill, no upscale
        elif mode == Resizer.RESIZE_TO_FILL:
            if original_smaller: # return src
                if not upscale:
                    return img
                else:
                    ratio = src[farthest_side] / dst[farthest_side]
                    new_size[farthest_side] = src[farthest_side]
                    new_size[closest_side] = floor(dst[closest_side] * ratio)
                    diff = src[closest_side] - new_size[closest_side]
                    offset[closest_side] = round(diff / 2)
                    box = (
                        offset[0], offset[1],
                        new_size[0] + offset[0], new_size[1] + offset[1]
                    )
                    img = img.crop(box)
                    return img.resize(dst, Image.LANCZOS)

            elif one_side_smaller:  # one crop the other
                if not upscale:
                    new_size[shorter_side] = src[shorter_side]
                    new_size[longer_side] = dst[longer_side]
                    diff = src[longer_side] - dst[longer_side]
                    offset[longer_side] = floor(diff / 2)
                    box = (
                        offset[0], offset[1],
                        new_size[0] + offset[0], new_size[1] + offset[1]
                    )
                    return img.crop(box)
                else:
                    ratio = src[shorter_side] / dst[shorter_side]
                    new_size[shorter_side] = src[shorter_side]
                    new_size[longer_side] = floor(dst[longer_side] * ratio)
                    diff = src[longer_side] - new_size[longer_side]
                    offset[longer_side] = round(diff / 2)
                    box = (
                        offset[0], offset[1],
                        new_size[0] + offset[0], new_size[1] + offset[1]
                    )
                    img = img.crop(box)
                    return img.resize(dst, Image.LANCZOS)

            elif original_bigger:
                if not upscale:
                    ratio = src[closest_side] / dst[closest_side]
                    new_size[closest_side] = src[closest_side]
                    new_size[farthest_side] = floor(dst[farthest_side] * ratio)
                    diff = src[farthest_side] - new_size[farthest_side]
                    offset[farthest_side] = round(diff / 2)
                    box = (
                        offset[0], offset[1],
                        new_size[0] + offset[0], new_size[1] + offset[1]
                    )
                    img = img.crop(box)
                    return img.resize(dst, Image.LANCZOS)
                else:
                    ratio = dst[closest_side] / src[closest_side]
                    new_size[closest_side] = src[closest_side]
                    new_size[farthest_side] = floor(dst[farthest_side] / ratio)
                    diff = src[farthest_side] - new_size[farthest_side]
                    offset[farthest_side] = round(diff / 2)
                    box = (
                        offset[0], offset[1],
                        new_size[0] + offset[0], new_size[1] + offset[1]
                    )
                    img = img.crop(box)
                    return img.resize(dst, Image.LANCZOS)

        # error out otherwise
        else:
            raise Exception('Invalid resize parameters')


