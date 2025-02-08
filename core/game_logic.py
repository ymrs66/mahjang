##game_logic.py
from core.constants import *

def handle_player_action_selection_phase(state, current_time):
    """
    プレイヤーのアクション選択フェーズ: ポン・チー・カンの確認
    """
    if not state.game.discards[1]:  # AIの捨て牌がない場合はスキップ
        print("[スキップ] AIの捨て牌がないためスキップ")
        state.transition_to(PLAYER_DRAW_PHASE)
        return

    discard_tile = state.game.discards[1][-1]
    actions = state.game.get_available_actions(0, discard_tile)

    if actions:
        print(f"[プレイヤーの選択フェーズ] 選択可能: {actions}")

        # ここで Wait Phase に飛ばすのではなく、ただ "state.available_actions" をセット
        # → イベントループで draw_action_buttons() が呼ばれてクリックを待つ
        state.available_actions = actions
        # ボタンは "events.events.handle_player_input()" や "handle_action_selection()" で処理
        print("[アクション選択ボタンを表示します]")
        return
    else:
        print("[プレイヤーの選択なし] 次のフェーズへ")
        state.ai_action_time = current_time + AI_ACTION_DELAY
        state.transition_to(AI_DRAW_PHASE)


def handle_ai_action_selection_phase(state, current_time):
    """
    AIのアクション選択フェーズ: ポン・チー・カンの判断
    """
    print("[AI アクション選択開始]")

    if not state.game.discards[0]:  # プレイヤーの捨て牌がない場合はスキップ
        print("[スキップ] プレイヤーの捨て牌がないためスキップ")
        state.transition_to(PLAYER_DRAW_PHASE)
        return

    discard_tile = state.game.discards[0][-1]

    # AIがポンできるかチェック
    if state.game.check_pon(1, discard_tile):
        print(f"[AIポン] {discard_tile} でポン")
        state.game.process_pon(1, state)
        return

    # AIがチーできるかチェック
    if state.game.check_chi(1, discard_tile):
        print(f"[AIチー] {discard_tile} でチー")
        state.game.process_chi(1, state.game.chi_candidates[0], state)
        return

    # AIがカンできるかチェック
    if state.game.check_kan(1, discard_tile):
        print(f"[AIカン] {discard_tile} でカン")
        state.game.process_kan(1, discard_tile, state, '明槓')
        return

    print("[AI アクションなし] プレイヤーのツモフェーズへ移行")
    state.transition_to(PLAYER_DRAW_PHASE)  # プレイヤーのツモフェーズ

def handle_pon_wait_phase(state, current_time):
    """
    ポン待機フェーズの処理
    """
    print("[ポン待機フェーズ] ポンを選択中")
    # ポンが決定された場合、処理を行う
    if state.pon_exec_flg:
        state.game.process_pon(0, state)
        state.pon_exec_flg = False
        state.transition_to(PLAYER_DISCARD_PHASE)
    elif state.skip_flg:
        print("ポンをスキップ")
        state.skip_flg = False
        state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズへ

def handle_chi_wait_phase(state, current_time):
    """
    チー待機フェーズの処理
    """
    print("[チー待機フェーズ] チーを選択中")
    if state.chi_exec_flg:
        print("チー実行")
        chosen_sequence = state.game.chi_candidates[0]  # 候補が複数あるなら選択処理を入れても良い
        state.game.process_chi(0, chosen_sequence, state)
        state.chi_exec_flg = False
        state.transition_to(PLAYER_DISCARD_PHASE)
    elif state.skip_flg:
        print("チーをスキップ")
        state.skip_flg = False
        state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズへ


def handle_kan_wait_phase(state, current_time):
    """
    カン待機フェーズの処理
    """
    print("[カン待機フェーズ] カンを選択中")
    if state.kan_exec_flg:
        kan_candidates = state.game.kan_candidates
        if kan_candidates:
            kan_tile = kan_candidates[0]
            kan_type = state.game.determine_kan_type(0, kan_tile)
            state.game.process_kan(0, kan_tile, state, kan_type)
            state.kan_exec_flg = False
            state.transition_to(PLAYER_DISCARD_PHASE)

    elif state.skip_flg:
        print("カンをスキップ")
        state.skip_flg = False
        state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズへ