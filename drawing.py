# drawing.py
import os
import pygame
from constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN, TILE_MARGIN_AI

def draw_tiles(screen, hand, tsumo_tile, selected_tile):
    """
    手牌を描画する。ポンした牌も右側に描画。
    """
    screen.fill((255, 255, 255))  # 背景を白で塗りつぶす

    # 手牌の描画
    for i, tile in enumerate(hand.tiles):
        x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN)
        y = 500
        screen.blit(tile.image, (x, y))
        if tile == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_WIDTH, TILE_HEIGHT), 3)

    # ツモ牌の描画
    if tsumo_tile:
        x = TILE_WIDTH + len(hand.tiles) * (TILE_WIDTH + TILE_MARGIN) + 20
        y = 500
        screen.blit(tsumo_tile.image, (x, y))
        if tsumo_tile == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_WIDTH, TILE_HEIGHT), 3)

    # ポンした牌の描画
    for i, pon_set in enumerate(hand.pons):
        for j, tile in enumerate(pon_set):
            x = TILE_WIDTH + (len(hand.tiles) + 1) * (TILE_WIDTH + TILE_MARGIN) + j * (TILE_WIDTH + TILE_MARGIN)
            y = 450 + i * (TILE_HEIGHT + 10)
            screen.blit(tile.image, (x, y))
            
def draw_ai_tiles(screen):
    for i in range(13):
        x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN_AI)
        y = 50
        ura_image = pygame.image.load("images/ura.png")
        screen.blit(ura_image, (x, y))

def draw_discards(screen, discards):
    for i, tile in enumerate(discards[0]):
        x = 200 + (i % 10) * (TILE_WIDTH + TILE_MARGIN)
        y = 300 + (i // 10) * (TILE_HEIGHT + TILE_MARGIN)
        screen.blit(tile.image, (x, y))

    for i, tile in enumerate(discards[1]):
        x = 850 - (i % 10) * (TILE_WIDTH + TILE_MARGIN)
        y = 150 + (i // 10) * (TILE_HEIGHT + TILE_MARGIN)
        rotated_image = pygame.transform.rotate(tile.image, 180)
        screen.blit(rotated_image, (x, y))

def draw_pon_button(screen, visible):
    """ポンボタンを描画し、その矩形を返す"""
    if visible:
        button_rect = pygame.Rect(TILE_WIDTH + 13 * (TILE_WIDTH + TILE_MARGIN), 500, 100, 50)  # ボタンの位置とサイズ
        pygame.draw.rect(screen, (255, 0, 0), button_rect)  # ボタンの赤い背景を描画

        # 日本語対応フォントを読み込む
        font_path = "meiryo.ttc"  # プロジェクトフォルダ内のフォントファイル

        font = pygame.font.Font(font_path, 36)

        text = font.render("ポン", True, (255, 255, 255))
        screen.blit(text, (button_rect.x + 20, button_rect.y + 10))  # テキストを描画
        return button_rect
    return None

def get_font_path(default="meiryo.ttc"):
    if os.path.exists(default):
        return default
    print("フォントが見つかりません。デフォルトフォントを使用します。")
    return None  # デフォルトフォントを使用