import random

import numpy as np
import pygame

import shape
from collision_detector import CollisionDetector
from ground import Ground
from tile import Tile


class Board:

    def __init__(self, screen, height=24, width=10):
        self.height = height
        self.width = width
        self._screen = screen
        self._ground = Ground(width, height)
        self._collision_detector = CollisionDetector(self, self._ground)
        self._matrix = np.zeros([width, height], dtype=int)
        self._current_tile = None
        self.score = 0
        self.game_over = False
        self._colours = shape.generate_colours()
        self._shapes = shape.generate_shapes()

    def draw(self):
        block_size = 35  # Set the size of the grid block
        x_offset = 100
        y_offset = 50
        
        # First draw all filled cells
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self._matrix[x, y] != 0:  # Only draw filled cells
                    rect = pygame.Rect(x_offset + x * block_size, y_offset + y * block_size, block_size, block_size)
                    pygame.draw.rect(self._screen, self._colours[self._matrix[x, y]], rect)
        
        # Then draw the grid lines for all cells in NAVY to match the board
        navy_color = self._colours[0]  # NAVY is the first color in the colors list
        for x in range(0, self.width + 1):
            pygame.draw.line(self._screen, navy_color,
                           (x_offset + x * block_size, y_offset),
                           (x_offset + x * block_size, y_offset + self.height * block_size))
        for y in range(0, self.height + 1):
            pygame.draw.line(self._screen, navy_color,
                           (x_offset, y_offset + y * block_size),
                           (x_offset + self.width * block_size, y_offset + y * block_size))

    def update(self, on_timer=True):
        if self._current_tile is None:
            self.create_tile()
        if on_timer:
            self.drop_tile()

        self._matrix[:, :] = 0
        self.draw_tile(self._current_tile)
        self.draw_ground(self._ground)
# check if tile locked and if so then don't move and merge with ground
    def drop_tile(self):
        is_locked = self._current_tile.move(0, 1)
        if is_locked:
            self._ground.merge(self._current_tile)
            self.score = self.score + self._ground.expire_rows()
            self.create_tile() # create new tile

    def create_tile(self):
        self._current_tile = Tile(self._collision_detector, self.get_shape(), self.get_colour(), random.randint(0, 6))

    def get_shape(self):
        return self._shapes[random.randint(0, len(self._shapes) - 1)]

    def get_colour(self):
        return random.randint(1, len(self._colours) - 1)

    def draw_tile(self, tile):
        matrix = tile.get_coordinates()
        for pos in matrix:
            if pos[1] < self.height:
                self._matrix[pos[0], pos[1]] = tile.get_color()

    def draw_ground(self, ground):
        self._matrix = np.maximum(self._matrix, ground.get_matrix())

    def on_key_up(self):
        if not self.game_over:
            self._current_tile.rotate(1)
            self.draw()

    def on_key_down(self):
        if not self.game_over:
            if self._current_tile.can_move(0, 1):
                self._current_tile.move(0, 1)
                self.draw()
            else:
                # If we can't move down, lock the piece
                self._ground.merge(self._current_tile)
                self.score = self.score + self._ground.expire_rows()
                self.create_tile()

    def on_key_left(self):
        if not self.game_over:
            self._current_tile.move(-1, 0)
            self.draw()

    def on_key_right(self):
        if not self.game_over:
            self._current_tile.move(1, 0)
            self.draw()
            
    def reset(self):
        """Reset the game board to its initial state"""
        self._ground = Ground(self.width, self.height)
        self._collision_detector = CollisionDetector(self, self._ground)
        self._matrix = np.zeros([self.width, self.height], dtype=int)
        self._current_tile = None
        self.score = 0
        self.game_over = False
        self.create_tile()