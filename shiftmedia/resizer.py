import magic
from PIL import Image
from PIL import ImageSequence
from PIL import ExifTags
import piexif
from math import floor
from shiftmedia import utils
from pprint import pprint as pp


class Resizer:
    """
    Resizer
    Handles resizing of local image files using different crop-factors.
    Supports resizing to fill or to fit with optional upscale for static
    images and animated GIFs.
    """

    # TODO: WRITE DOWN HOW MANUAL CROPS WORK IN GENERAL

    # Manual crops allow to choose target size, sample size
    # and specify position and where this sample will be taken from

    # Do we need to specify both target size and sample, or is target enough?
    # Yes, we need both. That will allow arbitrary crops.
    # Not just specifying non-centered position of sample.

    # How to deal with dst > src or more generically when sample size and
    # position goes outside of src?

    # Sample size must be proportional to target size.

    # SUMMARY: DEFINE sample PORTION OF src THAT WILL BECOME dst

    # Do we forbid to define sample outside of src?
    # Alternatively we can fallback to resizing intersection of src & sample:
    #    * Get intersection of sample and src
    #    * Find intersection center and its corresponding position in sample
    #    * Resize intersection to fill sample (exception if no upscale)
    #    * Resize result to become dst


    # TODO: IMPLEMENT MANUAL RESIZE
    # TODO: MAKE UNIVERSAL RESIZE METHOD
    # TODO: MAKE PATH TO PARAMS COMPATIBLE

    # resize modes (crop factor)
    RESIZE_TO_FILL = 'mode_resize_to_fill'
    RESIZE_TO_FIT = 'mode_resize_to_fit'

    @staticmethod
    def fix_orientation_and_save(src):
        """
        Fix orientation and save
        Check if file is an image and the checks it exif data for orientation.
        If the image is flipped, will attempt to fix its orientation while
        preserving original exif metadata.

        Note that this method uses quality parameter when saving rotated image.
        Thus if your image was modified by this function its size can increase.

        :param src: str, path to original.
        :return:str
        """
        if 'image' not in str(magic.from_file(src)).lower():
            return

        try:
            img = Image.open(src)
            if not getattr(img, '_getexif', None):
                return
        except OSError:
            return

        img, exif = Resizer.fix_orientation(img)
        if not exif:
            return

        # save params (some formats require quality)
        params = dict(exif=exif)
        if img.format == 'JPEG':
            params['quality'] = '95'

        # and save
        img.save(src, **params)

    @staticmethod
    def fix_orientation(img):
        """
        Fix orientation
        Accepts a PIL image and checks if orientation needs fixing. Upon
        success returns a tuple of the image object and patched exif data
        :param img: PIL.Image
        :return: (PIL.Image, exif bytes)
        """
        exif = piexif.load(img.info["exif"]) if 'exif' in img.info else None
        if not exif:
            return img, None

        fixable = [3, 6, 8]
        orientation_code = 274
        orientation = exif['0th'].get(orientation_code)
        if not orientation or orientation not in fixable:
            return img, None

        # fix now
        if orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 6:
            img = img.rotate(270, expand=True)
        elif orientation == 8:
            img = img.rotate(90, expand=True)

        # fix exif
        exif['0th'][orientation_code] = 1
        exif = piexif.dump(exif)

        # and return
        return img, exif

    @staticmethod
    def manual_crop(
        src,
        dst,
        src_size,
        dst_size,
        upscale=False,
        format=None,
        quality=100
    ):
        """
        Manual crop

        :param src:
        :param dst:
        :param src_size:
        :param dst_size:
        :param upscale:
        :param format:
        :param quality:
        :return:
        """
        pass

    def manual_crop_img(self, img, size, upscale=False):
        """
        Manual crop and return img
        Accepts source image (file or object) and target size. May optionally
        perform source image upscale in case it is smaller than dst.
        Does not write anything, but instead returns PIL.Image object which
        makes it reusable for gif sequence animations.

        :param img: Source file path or PIL.Image object
        :param size: Target size
        :param upscale: Whether to enlarge src if its smaller than dst
        :param write: Write to dst or return image object (for testing)
        :return: PIL.Image object
        """

        pass

    @staticmethod
    def auto_crop(
        src,
        dst,
        size,
        mode=None,
        upscale=False,
        format=None,
        quality=100
    ):
        """
        Resize auto crop
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
        img, exif = Resizer.fix_orientation(img)

        animated_gif = 'duration' in img.info and img.info['duration'] > 0
        if format:
            format = utils.extension_to_format(format) # normalize for pil

        if not animated_gif or (animated_gif and format and format != 'GIF'):
            # resize regular image
            if format == 'PNG' or dst.lower().endswith('.png'):
                img = img.convert(mode='RGBA')
            else:
                img = img.convert(mode='RGB')

            img = Resizer.auto_crop_img(img, size, mode, upscale)
            img.save(dst, format=format, quality=quality)
        else:
            # resize animated gif
            out = img.convert(mode='RGBA')
            out = Resizer.auto_crop_img(out, size, mode, upscale)
            frames = []
            for index, frame in enumerate(ImageSequence.Iterator(img)):
                if index == 0: continue
                frame = frame.convert(mode='RGBA')
                frame = Resizer.auto_crop_img(frame, size, mode, upscale)
                frames.append(frame)
            out.save(dst, format=format, save_all=True, append_images=frames)

        # and return
        return dst

    @staticmethod
    def auto_crop_img(img, size, mode=None, upscale=False):
        """
        Auto crop and return img
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


