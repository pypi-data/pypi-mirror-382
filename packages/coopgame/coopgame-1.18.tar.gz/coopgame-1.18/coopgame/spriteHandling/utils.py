import struct
import imghdr
from coopstructs.geometry.vectors.vectorN import Vector2
import ntpath
import os
from cooptools.transform import Transform
from typing import List, Tuple
import pygame
import cooptools.geometry_utils.vector_utils as vec

def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception:  # IGNORE:W0703
                return
        else:
            return
        return width, height

def image_at_rect(surf: pygame.Surface, rectangle, colorkey = None):
    """Load a specific image from a specific rectangle."""
    # Loads image from x, y, x+offset, y+offset.
    rect = pygame.Rect(rectangle)
    image = pygame.Surface(rect.size).convert()
    image.blit(surf, (0, 0), rect)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image


def image_at(surf: pygame.Surface, pos: Vector2, pixel_dims: Tuple[int, int], colorkey = None):
    """Load a specific image from a specific rectangle."""
    # Loads image from x, y, x+offset, y+offset.
    pixel_w, pixel_h = pixel_dims
    rectangle = (pos.x * pixel_w, pos.y * pixel_h, pixel_w, pixel_h)
    return image_at_rect(surf=surf, rectangle=rectangle, colorkey=colorkey)

def images_at(rects, colorkey = None):
    """Load a whole bunch of images and return them as a list."""
    return [image_at_rect(rect, colorkey) for rect in rects]

def try_load_sprite_file(filepath):
    try:
        return pygame.image.load(filepath).convert()
    except pygame.error as e:
        print(f"Unable to load spritesheet image: {filepath}: {e}")
        raise SystemExit(e)

def files_at_dir(directory):
    # iterate over files in
    # that directory
    ret = []
    for filename in os.scandir(directory):
        if filename.is_file():
            ret.append(rf"{directory}\{filename.name}")
    return ret

def path_and_file(filepath: str):
    head, tail = ntpath.split(filepath)
    tail = tail or ntpath.basename(head)
    return head, tail


def rename_files(filepaths: List[str], replace: List[Tuple[str, str]] = None):
    for path in filepaths:
        src = path
        path, filename = path_and_file(path)

        new = filename
        for rep in replace or []:
            new = new.replace(rep[0], rep[1])

        os.rename(src=src, dst=fr"{path}\{new}")

def scaled_rotation_point(transform: Transform) -> Tuple[float, ...]:
    return vec.hadamard_product(transform.Scale.Vector[0:2], transform.Rotation.RotationPoint[0:2])

def transform_sprite(surf: pygame.Surface, transform: Transform) -> Tuple[pygame.Surface, pygame.Rect]:
    # scale
    sprite_dims = surf.get_size()
    scale_vec = vec.hadamard_product(sprite_dims, transform.Scale.Vector[0:2])
    ret = pygame.transform.scale(surf, scale_vec)

    # rotate
    scaled_rot_point = scaled_rotation_point(transform)
    ret, rect = rotate_surface(surface=ret, angle=transform.Rotation.Degrees[0], pivot=scaled_rot_point)

    # translate
    rect.center = vec.add_vectors([rect.center, transform.Translation.Vector[0:2], tuple(-x for x in scaled_rot_point)])

    return (ret, rect)

def rotate_surface(surface, angle, pivot):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    start_rect = surface.get_rect()

    c_w = start_rect.width // 2
    if start_rect.width % 2 != 0: c_w += 1
    c_h = start_rect.height // 2
    if start_rect.height % 2 != 0: c_h += 1

    c = pygame.math.Vector2(c_w, c_h)
    # c = pygame.math.Vector2(*start_rect.center)

    rotateable_vector = c - pygame.math.Vector2(*pivot)
    rotated_vector = rotateable_vector.rotate(angle)
    rotated_surface = pygame.transform.rotate(surface, angle)
    rotated_surface_rect = rotated_surface.get_rect()

    relocation_vector = rotated_vector - rotateable_vector
    rotated_surface_rect.center = (c.x + relocation_vector.x, c.y - relocation_vector.y)

    return rotated_surface, rotated_surface_rect