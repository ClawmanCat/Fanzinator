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


def composite_paste(background, obj, where):
    max_w = max(background.size[0], where[0] + obj.size[0])
    max_h = max(background.size[1], where[1] + obj.size[1])

    expanded_background = PIL.Image.new(mode = 'RGBA', size = (max_w, max_h))
    expanded_background.paste(background, (0, 0))

    overlay = PIL.Image.new(mode = 'RGBA', size = (max_w, max_h))
    overlay.paste(obj, where)

    return PIL.Image.alpha_composite(expanded_background, overlay)


def find_image(target_name):
    for img_path in os.listdir('./assets'):
        name, ext = os.path.splitext(os.path.basename(img_path))

        if name == target_name and ext == '.png':
            return os.path.join('./assets', img_path)

    raise RuntimeError(f'No such image: {target_name}')


def make_sofa(on_sofa):
    sit_offset  = 250
    edge_offset = 80


    num_segments = len(on_sofa)
    if num_segments < 3: raise RuntimeError('Cannot build sofa with less than three segments.')


    segment_offsets = [ 386, 285, 286 ]
    segment_images  = list(map(lambda s: PIL.Image.open(f'./assets/couch_{s}.png'), ['l', 'm', 'r']))

    result = PIL.Image.new(
        mode = 'RGBA',
        size = ((
                segment_offsets[0] +
                ((num_segments - 3) * segment_offsets[1]) +
                segment_offsets[2] + segment_images[2].size[0]
            ),
            512
        )
    )

    total_offset = 0
    for i in range(num_segments):
        if   i == 0:                current_segment = segment_images[0]
        elif i == num_segments - 1: current_segment = segment_images[2]
        else:                       current_segment = segment_images[1]

        if   i == 0:                total_offset += 0
        elif i == 1:                total_offset += segment_offsets[0]
        elif i == num_segments - 1: total_offset += segment_offsets[2]
        else:                       total_offset += segment_offsets[1]

        fanzination_offset_w = total_offset + int(current_segment.size[0] / 2) - int(on_sofa[i].size[0] / 2)
        if i == 0: fanzination_offset_w += edge_offset
        if i == num_segments - 1: fanzination_offset_w -= edge_offset

        fanzination_offset_h = sit_offset - on_sofa[i].size[1]

        result = composite_paste(result, current_segment, (total_offset, 0))
        result = composite_paste(result, on_sofa[i], (fanzination_offset_w, fanzination_offset_h))

    return result


def make_fanzination(args):
    images = []

    for arg in args:
        if arg == 'flipped':
            if len(images) == 0: raise RuntimeError('The keyword flipped can only appear after the name of an image.')
            images[-1] = flip_image(images[-1])
        else:
            img = PIL.Image.open(find_image(arg))
            images.append(img)

    return combine_images(images)


def make_sofa_fanzination(args):
    on_sofa = []
    behind_sofa = []
    current_on_sofa = None

    for arg in args:
        if   arg == 'front': current_on_sofa = True
        elif arg == 'back':  current_on_sofa = False

        elif current_on_sofa is not None:
            img = PIL.Image.open(find_image(arg))

            if current_on_sofa: on_sofa.append(img)
            else: behind_sofa.append(img)
        else:
            RuntimeError('Fanzinations must be preceded by "front" to put them on the couch, or "back" to put them behind it.')

    sofa_image = make_sofa(on_sofa)
    background = combine_images(behind_sofa)

    new_sofa_w = int(background.size[0] * 0.90)
    new_sofa_h = int(sofa_image.size[1] / (sofa_image.size[0] / new_sofa_w))
    sofa_image = sofa_image.resize((new_sofa_w, new_sofa_h))

    return composite_paste(
        background,
        sofa_image,
        (
            int((background.size[0] - sofa_image.size[0]) / 2),
            int(background.size[1] * 0.66)
        )
    )