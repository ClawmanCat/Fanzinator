import PIL
import PIL.Image
import PIL.ImageOps

import os


def flip_image(img):
    return PIL.ImageOps.mirror(img)


def combine_images(images):
    w = 512; h = 128

    if len(images) > 3: w = 1024
    if len(images) > 6: raise RuntimeError('At most 6 images may be combined.')

    result = PIL.Image.new(mode = "RGBA", size = (w, h))

    for i, img in enumerate(images):
        iw, ih  = img.size
        scale   = h / ih
        resized = img.resize((int(iw * scale), h), PIL.Image.LANCZOS)

        center = ((i + 1) / (len(images) + 1)) * w
        left   = int(center - (resized.size[1] / 2))

        result.paste(resized, (left, 0))

    return result


def find_image(target_name):
    for img_path in os.listdir('./assets'):
        name, ext = os.path.splitext(os.path.basename(img_path))

        if name == target_name and ext == '.png':
            return os.path.join('./assets', img_path)

    raise RuntimeError(f'No such image: {target_name}')


def parse_and_combine(args):
    images = []

    for arg in args:
        if arg == 'flipped':
            if len(images) == 0: raise RuntimeError('The keyword flipped can only appear after the name of an image.')
            images[-1] = flip_image(images[-1])
        else:
            img = PIL.Image.open(find_image(arg))
            images.append(img)

    return combine_images(images)