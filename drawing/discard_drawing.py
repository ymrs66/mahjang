import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN

def draw_discards(screen, discards):
    """
    捨て牌を描画。
    """
    # プレイヤーの捨て牌 (discards[0])
    draw_discard_group(screen, discards[0], start_x=200, start_y=300, is_player=True)
    # AI の捨て牌 (discards[1])
    draw_discard_group(screen, discards[1], start_x=850, start_y=240, is_player=False)

def draw_discard_group(screen, tiles, start_x, start_y, is_player, max_per_row=10):
    current_x = start_x
    current_y = start_y
    count_in_row = 0

    for tile in tiles:
        if count_in_row == max_per_row:
            current_x = start_x
            # プレイヤーの場合は下方向、AIの場合は上方向にずらす
            current_y += (TILE_HEIGHT + TILE_MARGIN) if is_player else -(TILE_HEIGHT + TILE_MARGIN)
            count_in_row = 0

        if is_player:
            print("meld_discard",tile.is_meld_discard)
            if tile.is_riichi_discard or tile.is_meld_discard:
                rotated_img = pygame.transform.rotate(tile.image, 90)
                # 上方向に少しずらす
                screen.blit(rotated_img, (current_x, current_y + 10))
                current_x += (TILE_HEIGHT + TILE_MARGIN)  # 90°回転の場合、幅＝TILE_HEIGHT
            else:
                screen.blit(tile.image, (current_x, current_y))
                current_x += (TILE_WIDTH + TILE_MARGIN)
        else:
            # AIの場合
            # ここでは、チー・ポンで使用された牌は is_meld_discard が True であると想定
            if getattr(tile, "is_meld_discard", False):
                # 90°回転（例：時計回り90° → 90度回転）
                rotated_img = pygame.transform.rotate(tile.image, 90)
                # 調整例：Y座標を上に10ピクセルずらす
                screen.blit(rotated_img, (current_x, current_y - 10))
                # 90°回転の場合、画像の幅は TILE_HEIGHT に相当する
                current_x -= (TILE_HEIGHT + TILE_MARGIN)
            else:
                # 通常は180°回転
                rotated_img = pygame.transform.rotate(tile.image, 180)
                screen.blit(rotated_img, (current_x, current_y))
                current_x -= (TILE_WIDTH + TILE_MARGIN)

        count_in_row += 1
