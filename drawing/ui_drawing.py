##ui_drawing.py
import pygame
from core.constants import TILE_WIDTH, TILE_MARGIN, DEFAULT_FONT_PATH
from core.resource_utils import get_resource_path

def draw_pon_button(screen, visible):
    """
    ポンボタンを描画し、その矩形を返す。
    """
    if visible:
        button_rect = pygame.Rect(TILE_WIDTH + 13 * (TILE_WIDTH + TILE_MARGIN), 500, 100, 50)
        pygame.draw.rect(screen, (255, 0, 0), button_rect)

        font_path = get_resource_path(DEFAULT_FONT_PATH)
        if font_path:
            font = pygame.font.Font(font_path, 36)
            text = font.render("ポン", True, (255, 255, 255))
            screen.blit(text, (button_rect.x + 20, button_rect.y + 10))
        return button_rect
    return None