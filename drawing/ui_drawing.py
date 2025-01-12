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

def draw_chi_button(screen, visible):
    """
    チーボタンを描画し、その矩形を返す。
    """
    if visible:
        button_x = 900  # 手牌と重ならない右側の位置
        button_y = 450  # 画面下部の少し上
        button_width = 100
        button_height = 50

        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, (255, 255, 0), button_rect)  # 黄色のボタン

        font_path = get_resource_path(DEFAULT_FONT_PATH)
        if font_path:
            font = pygame.font.Font(font_path, 36)
            text = font.render("チー", True, (0, 0, 0))
            screen.blit(text, (button_rect.x + 20, button_rect.y + 10))
        return button_rect
    return None

def draw_kan_button(screen, visible, index=0, kan_candidate=None):
    """
    カンボタンを描画し、その矩形を返す。
    index: ボタンの位置
    kan_candidate: カン候補（表示用の牌情報）
    """
    if visible:
        button_rect = pygame.Rect(800, 500 + index * 60, 100, 50)
        pygame.draw.rect(screen, (0, 255, 0), button_rect)
        font_path = get_resource_path(DEFAULT_FONT_PATH)
        if font_path:
            font = pygame.font.Font(font_path, 20)
            text = font.render(f"カン: {kan_candidate}", True, (255, 255, 255))
            screen.blit(text, (button_rect.x + 5, button_rect.y + 10))
        return button_rect
    return None