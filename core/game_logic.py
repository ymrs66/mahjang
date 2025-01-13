##game_logic.py
from core.constants import *

def handle_draw_phase(state, current_time):
    if current_time >= state.draw_action_time:
        # ツモ牌を取得するが、手牌にはまだ追加しない
        state.tsumo_tile = state.game.draw_tile(0)
        print(f"ツモフェーズ: ツモ牌 = {state.tsumo_tile}")
        
        # ツモフェーズからプレイヤーの操作フェーズへ移行
        state.game.current_turn = PLAYER_DISCARD_PHASE  # プレイヤーのターン

        # 暗槓のチェック
        kan_candidates = state.game.check_kan(0)  # プレイヤーID 0
        if kan_candidates:
            print(f"暗槓候補: {kan_candidates}")
            state.game.can_kan = True
            state.game.kan_candidates = kan_candidates
            state.game.current_turn = KAN_WAIT_PHASE  # カン選択待機フェーズに移行
            return

        # 加槓のチェック（すでにポンしている牌との組み合わせ）
        for pon_set in state.game.players[0].pons:
            if len(pon_set) == 3 and state.tsumo_tile.suit == pon_set[0].suit and state.tsumo_tile.value == pon_set[0].value:
                print(f"加槓候補: {state.tsumo_tile}")
                state.game.can_kan = True
                state.game.kan_candidates = [state.tsumo_tile]
                state.game.current_turn = KAN_WAIT_PHASE  # カン選択待機フェーズに移行
                return

        # 通常のターンに移行
        state.game.current_turn = PLAYER_DISCARD_PHASE

def handle_ai_turn(state, current_time):
    """
    AIの動作を管理するターン。
    :param state: ゲームの状態
    :param current_time: 現在の時間
    """
    # プレイヤーのチーまたはポン待機中はAIの動作を停止
    if state.game.current_turn in [CHI_WAIT_PHASE, PON_WAIT_PHASE, KAN_WAIT_PHASE]: # 3: チー待機, 4: ポン待機, 5: カン待機
        print("プレイヤーが待機中のためAIの動作をスキップ")
        return

    # 通常のAI処理
    if current_time >= state.ai_action_time:
        # AIがカン可能か確認
        kan_candidates = state.game.check_kan(1)  # AIはプレイヤーID 1
        if kan_candidates:
            print(f"AIが暗槓を実行: {kan_candidates[0]}")
            state.game.process_kan(1, kan_candidates[0], '暗槓')
            state.ai_action_time = current_time + AI_ACTION_DELAY  # 次のAIアクションを待つ
            return  # カン後は即座にツモを行うため処理を終了

        # 明槓の可能性を確認（プレイヤーの捨て牌を対象に）
        if state.game.discards[0]:
            last_discard = state.game.discards[0][-1]
            if state.game.check_kan(1, last_discard):
                print(f"AIが明槓を実行: {last_discard}")
                state.game.process_kan(1, last_discard, '明槓')
                state.ai_action_time = current_time + AI_ACTION_DELAY
                return

        # 通常の捨て牌処理
        discard_tile = state.game.players[1].discard_tile()
        if discard_tile:
            state.game.discards[1].append(discard_tile)
            print(f"AIが牌を捨てました: {discard_tile}")

            # チーのチェックと処理
            if process_chi_logic(state, discard_tile):  # チー待機状態に移行
                state.game.current_turn = CHI_WAIT_PHASE  # チー待機状態
                return  # チー待機中はここで処理を終了

            # ポンのチェックと処理
            if process_pon_logic(state, discard_tile):  # ポン待機状態に移行
                state.game.current_turn = PON_WAIT_PHASE  # ポン待機状態
                return  # ポン待機中はここで処理を終了

            # チー・ポンが発生しない場合
            state.game.current_turn = PLAYER_DRAW_PHASE  # プレイヤーのツモフェーズに移行
            state.draw_action_time = current_time + AI_ACTION_DELAY
        else:
            print("AIの捨て牌がありません！")
            state.game.current_turn = PLAYER_DRAW_PHASE  # プレイヤーのツモフェーズに移行
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
        state.game.current_turn = PON_WAIT_PHASE  # ポン待機状態に移行
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