# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using
# sprite-sheets-and-drawing-the-background
# I've added some code to fail if the file wasn't found..
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)

# Additional notes
# - Further adaptations from https://www.pygame.org/wiki/Spritesheet
# - Cleaned up overall formatting.
# - Updated from Python 2 -> Python 3.

import pygame
import coopgame.spriteHandling.utils as utils
from typing import List

class SpriteSheet:

    def __init__(self, filename, n_rows, n_columns, x_margin_left=0, x_margin_right=None, x_padding=0,
                         y_margin_top=0, y_margin_bottom = None, y_padding=0):
        self.file_size = utils.get_image_size(filename)
        self.n_images_in_row = n_columns
        self.n_images_in_column = n_rows

        self.x_margin_left = x_margin_left
        self.x_margin_right = x_margin_right if x_margin_right else x_margin_left
        self.x_padding = x_padding
        self.y_margin_top = y_margin_top
        self.y_margin_bottom = y_margin_bottom if y_margin_bottom else y_margin_top
        self.y_padding = y_padding

        self.pixel_width = (self.file_size[0] - (self.x_margin_left + self.x_margin_right)
                         - (self.n_images_in_row - 1) * self.x_padding) // self.n_images_in_row
        self.pixel_height = (self.file_size[1] - (self.y_margin_top + self.y_margin_bottom)
                         - (self.n_images_in_column - 1) * self.y_padding) // self.n_images_in_column


        """Load the sheet."""
        self.sheet = utils.try_load_sprite_file(filepath=filename)

    def load_row_strip(self, row, colorkey = None, n_images: int = None) -> List[pygame.Surface]:
        grid_images = self.load_grid_images(colorkey=colorkey)

        if n_images is None or n_images < 0:
            return grid_images[row]
        else:
            return grid_images[row][:n_images]

    def load_column_strip(self, column, colorkey = None, n_images: int = None):
        grid_images = self.load_grid_images(colorkey=colorkey)

        images =  [row[column] for row in grid_images]
        if n_images is None or n_images < 0:
            return images
        else:
            return images[:n_images]

    def load_grid_images(self, colorkey = None):
        """Load a grid of images.
        x_margin is space between top of sheet and top of first row.
        x_padding is space between rows.
        Assumes symmetrical padding on left and right.
        Same reasoning for y.
        Calls self.images_at() to get list of images.
        """
        sheet_rect = self.sheet.get_rect()
        sheet_width, sheet_height = sheet_rect.size

        # To calculate the size of each sprite, subtract the two margins,
        #   and the padding between each row, then divide by num_cols.
        # Same reasoning for y.
        # x_sprite_size = (sheet_width - 2 * self.x_margin
        #                  - (self.n_images_in_row - 1) * self.x_padding) // self.n_images_in_row
        # y_sprite_size = (sheet_height - 2 * self.y_margin
        #                  - (self.n_images_in_column - 1) * self.y_padding) // self.n_images_in_column

        grid_images = []
        for row_num in range(self.n_images_in_column):
            grid_images.append([])
            for col_num in range(self.n_images_in_row):
                # Position of sprite rect is margin + one sprite size
                #   and one padding size for each row. Same for y.
                x = self.x_margin_left + col_num * (self.pixel_width + self.x_padding)
                y = self.y_margin_top + row_num * (self.pixel_height + self.y_padding)
                sprite_rect = x, y, self.pixel_width, self.pixel_height
                grid_images[row_num].append(utils.image_at_rect(surf=self.sheet, rectangle=sprite_rect, colorkey=colorkey))

        return grid_images