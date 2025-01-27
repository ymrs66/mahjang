##game_logic.py
from core.constants import *

def handle_player_draw_phase(state, current_time):
    # もしcurrent_time < state.ai_action_timeであれば、まだ待ち時間中とみなしてreturn
    if current_time < state.ai_action_time:
        return
    # まだツモっていないならツモする
    if True:
        tile = state.game.draw_tile(0)
        if tile:
            print(f"プレイヤーがツモ: {tile}")  # <- ここでまとめて出力
            state.game.players[0].add_tile(tile)
        else:
            print("山が空です。ゲーム終了")
            state.transition_to(GAME_END_PHASE)
            return
    # ツモ完了したら捨てるフェーズへ
    state.transition_to(PLAYER_DISCARD_PHASE)

def handle_player_discard_phase(state, current_time):
    print("[プレイヤー捨て牌フェーズ]")

    # フェーズに初めて来たときに waiting_for_player_discard を True にして、
    # まだ捨てていないならリターンする方法
    if not state.waiting_for_player_discard:
        print("[初回] プレイヤーの捨て牌待ちを開始します...")
        state.waiting_for_player_discard = True
        return

    # ここで waiting_for_player_discard が True なら、まだ入力中
    if state.waiting_for_player_discard:
        print("[待機] プレイヤーの捨て牌入力待ち...")
        return

    # ここに来た時点で waiting_for_player_discard = False → 入力完了

    discard_tile = state.game.discards[0][-1] if state.game.discards[0] else None
    if discard_tile:
        actions = state.game.get_available_actions(0, discard_tile)
        if actions:
            state.available_actions = actions
            state.transition_to(PLAYER_ACTION_SELECTION_PHASE)
            return

    # アクションがなければAIへ
    state.ai_action_time = current_time + AI_ACTION_DELAY
    state.transition_to(AI_DRAW_PHASE)

# game_logic.py

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

def handle_ai_draw_phase(state, current_time):
    """
    AIのツモフェーズを処理する
    """
    if current_time < state.ai_action_time:
        return  # AIの行動タイミングでなければスキップ

    print("[AIツモフェーズ] AIがツモを行います")

    # AIがツモを実行
    tile = state.game.draw_tile(1)
    if tile:
        state.game.players[1].draw_tile(tile)
        print(f"AIがツモ: {tile}")

    # カンの可能性を確認
    kan_candidates = state.game.check_kan(1)
    if kan_candidates:
        print(f"AIがカン可能: {kan_candidates}")
        state.game.process_kan(1, kan_candidates[0], state, "暗槓")
        state.ai_action_time = current_time + AI_ACTION_DELAY  # 次の行動まで遅延
        return

    # AIの捨てフェーズへ遷移
    state.transition_to(AI_DISCARD_PHASE)


def handle_ai_discard_phase(state, current_time):
    if current_time < state.ai_action_time:
        return
    
    discard_tile = state.game.players[1].discard_tile()
    if discard_tile:
        state.game.discards[1].append(discard_tile)
        print(f"AIが牌を捨てました: {discard_tile}")

    # ▼ 追加: プレイヤー(0)がAIの捨てた牌をポン/チー/カンできるかチェック
    actions = state.game.get_available_actions(player_id=0, discard_tile=discard_tile)
    if actions:
        # もしプレイヤーにポン/チー/カンの可能性があるなら、そちらを優先
        state.available_actions = actions
        state.transition_to(PLAYER_ACTION_SELECTION_PHASE)
        return

    # 次のアクションまでディレイ
    state.ai_action_time = current_time + AI_ACTION_DELAY

    # AIのアクション選択フェーズ → (本来はAIが他家の捨て牌に反応するためのロジックだが)
    # 現状2人打ちなら省略して、すぐプレイヤーのツモでもOK
##   state.transition_to(AI_ACTION_SELECTION_PHASE) //省略
    state.transition_to(PLAYER_DRAW_PHASE)  # プレイヤーのツモへ



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