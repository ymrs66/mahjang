##player_drawing.py
import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN,SCREEN_WIDTH,SCREEN_HEIGHT,DRAWN_TILE_EXTRA_OFFSET

def draw_player_state(screen, player, selected_tile,drawn_tile):
    """
    プレイヤーの手牌・ポン・チーの状態を描画する
    """
    # --- 手牌(13 or 14枚)を描画 ---
    for i, tile in enumerate(player.tiles):
        if tile == drawn_tile:
            x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN) + DRAWN_TILE_EXTRA_OFFSET
        else:
            # 14枚目の牌を描画する場合の位置調整
            x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN) 
        y = 500
        screen.blit(tile.image, (x, y))
        # 選択された手牌に赤枠を描画
        if tile == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_WIDTH, TILE_HEIGHT), 3)

    # ポン牌を描画
    pon_x = SCREEN_WIDTH - TILE_WIDTH * 3 - TILE_MARGIN * 3
    pon_y = 500
    print(f"[デバッグ] draw_player_state: player.pons={player.pons}") 
    for i, pon_set in enumerate(player.pons):
        print(f"[デバッグ]  pon_set index={i} => {pon_set}")       
        for j, tile in enumerate(pon_set):
            screen.blit(tile.image, (pon_x, pon_y - i * (TILE_HEIGHT + 10) - TILE_MARGIN))
            pon_x += TILE_WIDTH + TILE_MARGIN
        pon_x = SCREEN_WIDTH - TILE_WIDTH * 3 - TILE_MARGIN * 3

    # チー牌を描画
    chi_x = SCREEN_WIDTH - TILE_WIDTH * 6 - TILE_MARGIN * 6
    chi_y = 500
    for i, chi_set in enumerate(player.chis):
        for j, tile in enumerate(chi_set):
            screen.blit(tile.image, (chi_x, chi_y - i * (TILE_HEIGHT + 10) - TILE_MARGIN))
            chi_x += TILE_WIDTH + TILE_MARGIN
        chi_x = SCREEN_WIDTH - TILE_WIDTH * 6 - TILE_MARGIN * 6