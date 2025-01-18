##events.py

import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN, AI_TURN_PHASE, ACTION_SELECTION_PHASE, PLAYER_DISCARD_PHASE,AI_ACTION_DELAY 
from drawing.ui_drawing import draw_action_buttons

def handle_player_input(event, game, tsumo_tile, selected_tile, current_time, state, screen):
    """
    プレイヤーの入力処理
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        print(f"[クリック検出] 座標: {pos}")

        # 手牌のクリック処理
        for i, tile in enumerate(game.players[0].tiles):
            x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN)
            y = 500
            if x <= pos[0] <= x + TILE_WIDTH and y <= pos[1] <= y + TILE_HEIGHT:
                selected_tile = tile
                print(f"[選択] 手牌から選択された牌: {selected_tile}")
                return tsumo_tile, selected_tile

        # ツモ牌のクリック処理
        if tsumo_tile:
            x = TILE_WIDTH + len(game.players[0].tiles) * (TILE_WIDTH + TILE_MARGIN) + 20
            y = 500
            if x <= pos[0] <= x + TILE_WIDTH and y <= pos[1] <= y + TILE_HEIGHT:
                selected_tile = tsumo_tile
                print(f"[選択] ツモ牌を選択: {selected_tile}")
                return tsumo_tile, selected_tile

    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        print(f"[スペースキー押下] 選択された牌: {selected_tile}")

        if selected_tile is None:
            print("[警告] 牌が選択されていません。捨て牌処理をスキップします。")
            return tsumo_tile, selected_tile

        # **捨て牌処理**
        print(f"[捨て牌前] 手牌: {game.players[0].tiles}")

        if selected_tile == tsumo_tile:
            print(f"[処理] ツモ牌を捨てます: {selected_tile}")
            game.discard_tile(selected_tile, 0)
            tsumo_tile = None  # **ツモ牌をクリア**
        else:
            print(f"[処理] 手牌から捨てます: {selected_tile}")
            if selected_tile in game.players[0].tiles:  # **エラーチェック**
                game.players[0].tiles.remove(selected_tile)  # **手牌から削除**
                game.discard_tile(selected_tile, 0)
            else:
                print(f"[エラー] {selected_tile} は手牌に存在しません。処理をスキップ")
                return tsumo_tile, selected_tile  # **手牌にない場合は処理せず戻る**

            # **ツモ牌を手牌に追加**
            if tsumo_tile:
                print(f"[処理] ツモ牌を手牌に追加: {tsumo_tile}")
                game.players[0].add_tile(tsumo_tile)
                tsumo_tile = None  # **ツモ牌をリセット**

        print(f"[捨て牌後] 手牌: {game.players[0].tiles}")
        print(f"[捨て牌リスト] {game.discards[0]}")

        # **手牌の並び替え**
        game.players[0].sort_tiles()
        print(f"[並び替え後の手牌] {game.players[0].tiles}")

        # **捨て牌後にアクション選択が必要か確認**
        discard_tile = game.discards[0][-1] if game.discards[0] else None
        if discard_tile:
            actions = game.get_available_actions(0, discard_tile)
            print(f"[アクション候補] {actions}")

            if actions:
                state.available_actions = actions
                state.action_buttons = draw_action_buttons(screen, actions)
                state.transition_to(ACTION_SELECTION_PHASE)  # **アクション選択フェーズへ**
                return tsumo_tile, selected_tile

        # **アクションがない場合は AI のターンへ**
        print("[処理] アクションなし → AIのターンへ移行（ディレイ付き）")
        state.ai_action_time = current_time + AI_ACTION_DELAY  # **ディレイを設定**
        state.transition_to(AI_TURN_PHASE)

    return tsumo_tile, selected_tile  # **修正: すべてのケースで戻り値を保証**
