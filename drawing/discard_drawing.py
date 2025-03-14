##discard_drawing.py
import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN

def draw_discards(screen, discards):
    """
    捨て牌を描画。
    """
    # プレイヤーの捨て牌
def draw_discards(screen, discards):
    current_x = 200
    current_y = 300
    count_in_row = 0

    for tile in discards[0]:
        # 行が10枚たまったら折り返し:
        if count_in_row == 10:
            current_x = 200
            current_y += (TILE_HEIGHT + TILE_MARGIN)
            count_in_row = 0

        if tile.is_riichi_discard: #リーチ時捨て牌を90°回転
            rotated_img = pygame.transform.rotate(tile.image, 90)
            # 上方向に少しずらす (例: 10px)
            screen.blit(rotated_img, (current_x, current_y + 10))
            # 次の牌は “横幅” として TILE_HEIGHT を使う
            current_x += (TILE_HEIGHT + TILE_MARGIN)
        else:
            # 通常
            screen.blit(tile.image, (current_x, current_y))
            # 次の牌は “横幅” として TILE_WIDTH を使う
            current_x += (TILE_WIDTH + TILE_MARGIN)

        count_in_row += 1


    # AIの捨て牌
    current_x = 850
    current_y = 240
    count_in_row = 0

    for tile in discards[1]:
    # 行が10枚たまったら折り返し:
        if count_in_row == 10:
            current_x = 850
            current_y -= (TILE_HEIGHT + TILE_MARGIN)
            count_in_row = 0

        if tile.is_riichi_discard == 2: # aiのリーチは「2」 とする
            ai_rotated_img = pygame.transform.rotate(tile.image, 270)
            # 下方向に少しずらす (例: 10px)
            screen.blit(ai_rotated_img, (current_x, current_y - 10))
            # 次の牌は “横幅” として TILE_HEIGHT を使う
            current_x -= (TILE_HEIGHT + TILE_MARGIN)
        else:
            # 通常
            ai_img = pygame.transform.rotate(tile.image, 180)
            screen.blit(ai_img, (current_x, current_y))
            # 次の牌は “横幅” として TILE_WIDTH を使う
            current_x -= (TILE_WIDTH + TILE_MARGIN)

        count_in_row += 1
