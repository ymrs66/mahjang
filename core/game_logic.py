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
    AIの動作を管理するターン。
    :param state: ゲームの状態
    :param current_time: 現在の時間
    """
    # プレイヤーのチーまたはポン待機中はAIの動作を停止
    if state.game.current_turn in [3, 4]:  # 3: チー待機, 4: ポン待機
        print("プレイヤーが待機中のためAIの動作をスキップ")
        return

    # 通常のAI処理
    if current_time >= state.ai_action_time:
        discard_tile = state.game.players[1].discard_tile()
        if discard_tile:
            state.game.discards[1].append(discard_tile)
            print(f"AIが牌を捨てました: {discard_tile}")

            # チーのチェックと処理
            if process_chi_logic(state, discard_tile):  # チー待機状態に移行
                state.game.current_turn = 3  # チー待機状態
                return  # チー待機中はここで処理を終了

            # ポンのチェックと処理
            if process_pon_logic(state, discard_tile):  # ポン待機状態に移行
                state.game.current_turn = 4  # ポン待機状態
                return  # ポン待機中はここで処理を終了

            # チー・ポンが発生しない場合
            state.game.current_turn = 2  # プレイヤーのツモフェーズに移行
            state.draw_action_time = current_time + AI_ACTION_DELAY
        else:
            print("AIの捨て牌がありません！")
            state.game.current_turn = 2  # プレイヤーのツモフェーズに移行
            state.draw_action_time = current_time + AI_ACTION_DELAY

        # 次のAI行動タイミングを設定
        state.ai_action_time = current_time + AI_ACTION_DELAY
        
def process_pon_logic(state, discard_tile):
    """
    ポンの処理を行うロジック（選択を待機する）
    """
    pon_candidates = state.game.check_pon(0, discard_tile)
    if pon_candidates:
        print(f"ポンの選択待機中: {discard_tile}")
        state.game.can_pon = True
        state.game.pon_candidates = pon_candidates  # ポン候補を設定
        state.game.target_tile = discard_tile
        state.game.current_turn = 3  # ポン待機状態に移行
        return True
    else:
        print("ポン候補がありません。")
        state.game.can_pon = False
        state.game.pon_candidates = []
        return False

def process_chi_logic(state, discard_tile):
    """
    チーロジックを処理する。チー待機フェーズに移行する場合はTrueを返す。
    """
    print("=== チーロジック開始 ===")
    print(f"プレイヤーの手番: {state.game.current_turn}, 捨て牌: {discard_tile}")

    # プレイヤーのチー可能性を確認
    chi_candidates = state.game.check_chi(0, discard_tile)  # プレイヤーIDは0で固定
    if chi_candidates:
        print(f"チー候補が見つかりました: {chi_candidates}")
        state.game.can_chi = True
        state.game.chi_candidates = chi_candidates
        return True

    print("チー候補がありません。")
    return False