##events.py

import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN,AI_TURN_PHASE

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

        # 捨て牌処理を追加
        if selected_tile:
            print(f"プレイヤーが捨てた牌: {selected_tile}")
            print(f"捨てる前の手牌: {game.players[0].tiles}")
            game.discard_tile(selected_tile, 0)  # プレイヤーIDは0
            print(f"捨てた後の手牌: {game.players[0].tiles}")
            print(f"現在の捨て牌: {game.discards[0]}")

        if tsumo_tile:
            # ツモ牌がすでに捨てられているかを確認
            if tsumo_tile in game.discards[0]:
                print(f"ツモ牌 {tsumo_tile} (id={id(tsumo_tile)}) は既に捨て牌リストに存在します: {game.discards[0]}")
            else:
                print(f"ツモ牌を手牌に追加: {tsumo_tile}")
                print(f"追加前の手牌: {game.players[0].tiles}")
                game.players[0].add_tile(tsumo_tile)
                game.players[0].sort_tiles()
                print(f"追加後の手牌: {game.players[0].tiles}")
            tsumo_tile = None
        
        game.current_turn = AI_TURN_PHASE  # AIのターンに移行
        selected_tile = None

    return tsumo_tile, selected_tile
