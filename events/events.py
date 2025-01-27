##events.py

import pygame
from core.constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN, AI_DRAW_PHASE, PLAYER_ACTION_SELECTION_PHASE, PLAYER_DISCARD_PHASE,AI_ACTION_DELAY
from drawing.ui_drawing import draw_action_buttons

def handle_player_input(event, game, selected_tile, current_time, state, screen):
    """
    プレイヤーの入力処理（詳細なデバッグログ付き）
    """
    print(f"[デバッグ] イベント検出: {event}")

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

    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        # スペースキーが押されたら ...
        if selected_tile is not None and selected_tile in game.players[0].tiles:
            print(f"[処理] 手牌から捨てます: {selected_tile}")
            game.discard_tile(selected_tile, 0)

            # discard後は選択牌をリセットしておかないと再捨ての原因になる
            state.selected_tile = None

            # ✅ **プレイヤーの捨て牌完了を明示**
            state.waiting_for_player_discard = False

            # **捨て牌後にアクション選択が必要か確認**
            discard_tile = game.discards[0][-1] if game.discards[0] else None
            if discard_tile:
                actions = game.get_available_actions(0, discard_tile)
                print(f"[アクション候補] {actions}")

                if actions:
                    # actions = ["ポン", "チー", "カン"] など
                    state.available_actions = actions
                    state.action_buttons = draw_action_buttons(screen, actions)
                    state.transition_to(PLAYER_ACTION_SELECTION_PHASE)
                    return selected_tile

            # ✅ **AIのターンが適切に進むように制御**
            state.ai_action_time = current_time + AI_ACTION_DELAY
            print(f"[フェーズ遷移] AI_DRAW_PHASE へ移行")
            state.transition_to(AI_DRAW_PHASE)
        else:
            # 選択された牌がない場合、捨て牌を行えないため、警告を表示
            print("[警告] 捨てる牌が選択されていません。牌を選択してください。")
            # 必要に応じて、ユーザーに牌を選択するよう促すUIを追加
            # ここでは何もしない
            pass

    return selected_tile