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
    print("[AI アクション選択開始]")

    # プレイヤーの捨て牌が無ければスキップ
    if not state.game.discards[0]:
        print("[スキップ] プレイヤーの捨て牌がないためスキップ")
        state.transition_to(PLAYER_DRAW_PHASE)
        return

    # プレイヤーの捨て牌のうち直近の1枚を取得
    discard_tile = state.game.discards[0][-1]

    # (1) AIが取り得るアクションをまとめて取得
    actions = state.game.get_available_actions(player_id=1, discard_tile=discard_tile)
    print(f"[AI] 行動候補: {actions}")

    # (2) アクションがあるなら、優先度 or ランダム で1つ実行
    if "ポン" in actions:
        print("[AI] ポンを選択")
        state.game.process_pon(1, state)
        return
    elif "チー" in actions:
        print("[AI] チーを選択")
        chosen_sequence = state.game.meld_candidates["chi"][0]  # とりあえず先頭
        state.game.process_chi(1, chosen_sequence, state)
        return
    elif "カン" in actions:
        print("[AI] カンを選択")
        kan_tile = state.game.meld_candidates["kan"][0]  # とりあえず先頭
        state.game.process_kan(1, kan_tile, state)
        return

    # (3) どのアクションも無ければスキップ
    print("[AI アクションなし] → プレイヤーのツモへ")
    state.transition_to(PLAYER_DRAW_PHASE)

def handle_meld_wait_phase(state, current_time):
    """
    ポン／チー／カン待機フェーズを共通処理で行う。
    state.current_phase を見て分岐し、実行 or スキップの処理を行う。
    """
    # ログなど共通処理
    print("[待機フェーズ] ポン or チー or カン待ちフェーズです")
    
    if state.meld_action == "skip":
        # 全待機共通でスキップ処理
        print("[スキップ] メルドを行わずツモへ")
        state.meld_action = None  # リセット
        state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズへ
        return