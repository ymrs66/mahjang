##game_logic.py
from core.constants import AI_ACTION_DELAY

def handle_draw_phase(state, current_time):
    """
    プレイヤーが牌をツモるフェーズ
    """
    if current_time >= state.draw_action_time:
        state.tsumo_tile = state.game.draw_tile(0)
        state.game.current_turn = 0

def handle_ai_turn(state, current_time):
    """
    AIの動作を管理するターン
    """
    if current_time >= state.ai_action_time:
        discard_tile = state.game.players[1].discard_tile()
        if discard_tile:
            state.game.discards[1].append(discard_tile)
            print(f"AIが牌を捨てました: {discard_tile}")

            # ポンのチェックと処理
            if process_pon_logic(state, discard_tile):
                return  # ポン待機状態に移行した場合はここで終了

            state.game.current_turn = 2  # ツモフェーズに移行
            state.draw_action_time = current_time + AI_ACTION_DELAY
        else:
            print("AIの捨て牌がありません！")
            state.game.current_turn = 2
            state.draw_action_time = current_time + AI_ACTION_DELAY

        state.ai_action_time = current_time + AI_ACTION_DELAY

def process_pon_logic(state, discard_tile):
    """
    ポンの処理を行うロジック（選択を待機する）
    """
    if state.game.check_pon(0, discard_tile):
        print(f"ポンの選択待機中: {discard_tile}")
        state.game.can_pon = True
        state.game.target_tile = discard_tile
        state.game.current_turn = 3  # ポン待機状態に移行
        return True
    return False