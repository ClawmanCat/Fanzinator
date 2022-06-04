import PIL
import PIL.Image
import PIL.ImageOps

import os


def flip_image(img):
    return PIL.ImageOps.mirror(img)


def combine_images(images):
    w = 512; h = 128
    result = PIL.Image.new(mode = "RGBA", size = (w, h))

    global_scale = 1 + ((len(images) - 1) // 3)

    for i, img in enumerate(images):
        # Image should be resized such that its height is h / global_scale.
        iw, ih  = img.size

        scale   = h / (ih * global_scale)
        resized = img.resize((int(iw * scale), int(ih * scale)), PIL.Image.LANCZOS)

        center = ((i + 1) / (len(images) + 1)) * w
        left   = int(center - (resized.size[0] / 2))
        top    = int(0.5 * h) - int(0.5 * resized.size[1])

        result.paste(resized, (left, top))

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