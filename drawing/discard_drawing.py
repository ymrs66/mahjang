##discard_drawing.py
import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN

def draw_discards(screen, discards):
    """
    捨て牌を描画。
    """
    # プレイヤーの捨て牌
    for i, tile in enumerate(discards[0]):
        x = 200 + (i % 10) * (TILE_WIDTH + TILE_MARGIN)
        y = 300 + (i // 10) * (TILE_HEIGHT + TILE_MARGIN)
        screen.blit(tile.image, (x, y))

    # AIの捨て牌
    for i, tile in enumerate(discards[1]):
        x = 850 - (i % 10) * (TILE_WIDTH + TILE_MARGIN)
        y = 150 + (i // 10) * (TILE_HEIGHT + TILE_MARGIN)
        rotated_image = pygame.transform.rotate(tile.image, 180)
        screen.blit(rotated_image, (x, y))