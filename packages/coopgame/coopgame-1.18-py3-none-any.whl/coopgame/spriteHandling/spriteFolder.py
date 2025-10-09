import os
import pygame
import coopgame.spriteHandling.utils as utils

class SpriteFolderHandler:

    def __init__(self, dir, delim: str = "__"):
        if not pygame.get_init():
            pygame.init()
            pygame.display.set_mode((800, 600))

        self.poses = {}
        files = os.listdir(dir)

        for file in files:
            name_attrs = file.split(delim)
            if len(name_attrs) > 2:
                pose = '_'.join(name_attrs[0:2])
            else:
                pose = f"{name_attrs[0]}"

            self.poses.setdefault(pose, [])
            self.poses[pose].append(utils.try_load_sprite_file(filepath=f"{dir}\{file}"))

if __name__ == "__main__":
    from pprint import pprint
    sfh = SpriteFolderHandler(r'C:\Users\tburns\Downloads\ninjaadventurenew\png')
    pprint(sfh.poses)