##ai_drawing.py
import pygame
from core.constants import TILE_WIDTH, TILE_MARGIN_AI, AI_TILE_BACK_IMAGE

def draw_ai_tiles(screen):
    """
    AIの手牌（裏面）を描画。
    """
    ura_image = pygame.image.load(AI_TILE_BACK_IMAGE)
    for i in range(13):
        x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN_AI)
        y = 50
        screen.blit(ura_image, (x, y))