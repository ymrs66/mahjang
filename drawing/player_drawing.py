##player_drawing.py
import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN, PON_OFFSET_X, PON_OFFSET_Y,SCREEN_HEIGHT

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
    ポンまたはチーした牌を描画。
    """
    for i, pon_set in enumerate(hand.pons):
        for j, tile in enumerate(pon_set):
            if tile.image is None:
                print(f"警告: 牌 {tile.suit}{tile.value} の画像が設定されていません")
                continue  # 画像がない牌はスキップ

            x = TILE_WIDTH + (len(hand.tiles) + 1 + j) * (TILE_WIDTH + TILE_MARGIN)
            y = 450 + i * (TILE_HEIGHT + 10)
            screen.blit(tile.image, (x, y))

def draw_chis(screen, player):
    """
    チーした牌を画面に描画する。
    """
    x = 200  # 描画開始位置（ポンとずらすため）
    y = SCREEN_HEIGHT - TILE_WIDTH - TILE_MARGIN  # 下部に配置

    for sequence in player.chis:
        for tile in sequence:
            screen.blit(tile.image, (x, y))
            x += TILE_WIDTH + TILE_MARGIN  # 牌間隔を調整
        x += TILE_MARGIN * 2  # 順子間の間隔を調整