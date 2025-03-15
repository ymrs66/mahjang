##player_drawing.py
import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN,SCREEN_WIDTH,SCREEN_HEIGHT,DRAWN_TILE_EXTRA_OFFSET

def draw_player_state(screen, player, selected_tile, drawn_tile):
    # --- 手牌（13 or 14枚）を描画 ---
    for i, tile in enumerate(player.tiles):
        if tile == drawn_tile:
            x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN) + 20  # DRAWN_TILE_EXTRA_OFFSET=20
        else:
            x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN)
        y = 500
        screen.blit(tile.image, (x, y))
        if tile == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_WIDTH, TILE_HEIGHT), 3)

    # --- ポン牌を描画 ---
    pon_x = SCREEN_WIDTH - TILE_WIDTH * 3 - TILE_MARGIN * 3
    pon_y = 500
    for i, pon_set in enumerate(player.pons):
        for j, tile in enumerate(pon_set):
            # 例として、ポン牌も横に回転する場合
            if tile.is_meld_discard:
                rotated_img = pygame.transform.rotate(tile.image, 90)
                screen.blit(rotated_img, (pon_x, pon_y - i * (TILE_HEIGHT + 10) - TILE_MARGIN + 10))
                pon_x += TILE_HEIGHT + TILE_MARGIN
            else:
                screen.blit(tile.image, (pon_x, pon_y - i * (TILE_HEIGHT + 10) - TILE_MARGIN))
                pon_x += TILE_WIDTH + TILE_MARGIN
        pon_x = SCREEN_WIDTH - TILE_WIDTH * 3 - TILE_MARGIN * 3

    # --- チー牌を描画 ---
    chi_x = SCREEN_WIDTH - TILE_WIDTH * 6 - TILE_MARGIN * 6
    chi_y = 500
    for i, chi_set in enumerate(player.chis):
        for j, tile in enumerate(chi_set):
            # もしメルドとして使用された（チーした）牌なら90°回転して横に表示
            if tile.is_meld_discard:
                rotated_img = pygame.transform.rotate(tile.image, 90)
                # Y座標を上に10ピクセルずらす（必要に応じて調整）
                screen.blit(rotated_img, (chi_x, chi_y - i * (TILE_HEIGHT + 10) - TILE_MARGIN + 10))
                # 90°回転の場合、画像の幅はTILE_HEIGHTとなる
                chi_x += TILE_HEIGHT + TILE_MARGIN
            else:
                screen.blit(tile.image, (chi_x, chi_y - i * (TILE_HEIGHT + 10) - TILE_MARGIN))
                chi_x += TILE_WIDTH + TILE_MARGIN
        chi_x = SCREEN_WIDTH - TILE_WIDTH * 6 - TILE_MARGIN * 6