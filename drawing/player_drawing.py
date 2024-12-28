##player_drawing.py
import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN, PON_OFFSET_X, PON_OFFSET_Y

def draw_tiles(screen, hand, tsumo_tile, selected_tile):
    """
    プレイヤーの手牌とツモ牌を描画。
    """
    for i, tile in enumerate(hand.tiles):
        x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN)
        y = 500
        screen.blit(tile.image, (x, y))
        if tile == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_WIDTH, TILE_HEIGHT), 3)

    if tsumo_tile:
        x = TILE_WIDTH + len(hand.tiles) * (TILE_WIDTH + TILE_MARGIN) + 20
        y = 500
        screen.blit(tsumo_tile.image, (x, y))
        if tsumo_tile == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_WIDTH, TILE_HEIGHT), 3)

def draw_pons(screen, hand):
    """
    ポンした牌を描画
    """
    for i, pon_set in enumerate(hand.pons):
        for j, tile in enumerate(pon_set):
            x = TILE_WIDTH + (len(hand.tiles) + 1) * (TILE_WIDTH + TILE_MARGIN) + j * (TILE_WIDTH + TILE_MARGIN) + PON_OFFSET_X
            y = PON_OFFSET_Y + i * (TILE_HEIGHT + 10)
            screen.blit(tile.image, (x, y))