##events.py

import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN

def handle_player_input(event, game, tsumo_tile, selected_tile, current_time):
    """
    プレイヤーの入力処理
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        for i, tile in enumerate(game.players[0].tiles):
            x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN)
            y = 500
            if x <= pos[0] <= x + TILE_WIDTH and y <= pos[1] <= y + TILE_HEIGHT:
                selected_tile = tile
                print(f"手牌から選択された牌: {selected_tile}")

        if tsumo_tile:
            x = TILE_WIDTH + len(game.players[0].tiles) * (TILE_WIDTH + TILE_MARGIN) + 20
            y = 500
            if x <= pos[0] <= x + TILE_WIDTH and y <= pos[1] <= y + TILE_HEIGHT:
                selected_tile = tsumo_tile
                print(f"ツモ牌から選択された牌: {selected_tile}")

    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        print(f"スペースキーが押されました。選択された牌: {selected_tile}")
        if selected_tile is None:
            print("警告: 牌が選択されていません。捨て牌処理をスキップします。")
            return tsumo_tile, selected_tile

        if selected_tile == tsumo_tile:
            print(f"捨てたツモ牌: {tsumo_tile}")
            game.discards[0].append(tsumo_tile)
            tsumo_tile = None
        elif selected_tile in game.players[0].tiles:
            print(f"捨てた手牌: {selected_tile}")
            game.discards[0].append(selected_tile)
            game.players[0].remove_tile(selected_tile)
        else:
            print(f"エラー: {selected_tile} は手牌にもツモ牌にも存在しません！")

        if tsumo_tile:
            print(f"ツモ牌を手牌に追加: {tsumo_tile}")
            game.players[0].add_tile(tsumo_tile)
            game.players[0].sort_tiles()
            tsumo_tile = None

        game.current_turn = 1
        selected_tile = None

    return tsumo_tile, selected_tile

def handle_pon_click(event, button_rect, game):
    """
    ポンボタンがクリックされた場合の処理。
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        if button_rect and button_rect.collidepoint(pos):
            game.process_pon(0)  # ポン処理
            return True
    return False