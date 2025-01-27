import pygame
from events.events import handle_player_input
from core.constants import *  # 全ての定義をインポート
from drawing.ui_drawing import draw_pon_button, draw_chi_button,draw_kan_button

def handle_events(state, current_time, screen):
    print(f"[デバッグ] 現在のフェーズ: {state.current_phase}")

    for event in pygame.event.get():
        print(f"[デバッグ] イベント取得: {event}")

        if event.type == pygame.QUIT:
            print("[処理] ゲーム終了")
            return False

        # --- ① プレイヤーの手牌クリック関連 ---
        if state.current_phase in [PLAYER_DISCARD_PHASE, PLAYER_DRAW_PHASE]:
            # ここで state.selected_tile などを更新
            selected_tile  = handle_player_input(
                event,
                state.game,
                state.selected_tile,
                current_time,
                state,
                screen
            )
            # 戻り値から更新
            state.selected_tile = selected_tile

        # --- ② ACTION_SELECTION_PHASE 用に handle_action_selection を呼ぶ ---
        if state.current_phase == PLAYER_ACTION_SELECTION_PHASE:
            handle_action_selection(event, state,current_time)

        # --- ③ ポン・チー・カン待機フェーズのボタン処理 ---
        if state.current_phase in [PON_WAIT_PHASE, CHI_WAIT_PHASE, KAN_WAIT_PHASE]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state.current_phase == PON_WAIT_PHASE and state.pon_button_rect and state.pon_button_rect.collidepoint(event.pos):
                    print("ポンボタンが押されました")
                    state.pon_exec_flg = True
                elif state.current_phase == CHI_WAIT_PHASE and state.chi_button_rect and state.chi_button_rect.collidepoint(event.pos):
                    print("チーボタンが押されました")
                    state.chi_exec_flg = True
                elif state.current_phase == KAN_WAIT_PHASE and state.kan_button_rect and state.kan_button_rect.collidepoint(event.pos):
                    print("カンボタンが押されました")
                    state.kan_exec_flg = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                print("スキップ処理（スペースキー）")
                state.skip_flg = True

    return True

# event_handler.py にある handle_action_selection を再掲＆修正

def handle_action_selection(event, state, current_time):
    """
    アクション選択フェーズ(PLAYER_ACTION_SELECTION_PHASE)で、
    表示中のボタンをクリックしてどれを実行するかを決定する。
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        # 各アクションのボタン領域をループ
        for action, rect in state.action_buttons.items():
            if rect.collidepoint(event.pos):
                print(f"[クリックされたアクション]: {action}")

                if action == "ポン":
                    # ポンできるかどうかをチェック
                    if state.game.can_pon:
                        print("[処理] ポンを実行します。")
                        state.game.process_pon(0, state)
                        state.transition_to(PLAYER_DISCARD_PHASE)
                    else:
                        print("[エラー] ポンできない状態なのにボタンが押されました。")

                elif action == "チー":
                    # チーできるかどうかをチェック
                    if state.game.can_chi and state.game.chi_candidates:
                        # ここでは候補が一つの場合のみ処理
                        # 複数ある場合は別途UIなどで選んでもらうようにする
                        chosen_sequence = state.game.chi_candidates[0]
                        print(f"[処理] チーを実行します。順子: {chosen_sequence}")
                        state.game.process_chi(0, chosen_sequence, state)
                        state.transition_to(PLAYER_DISCARD_PHASE)
                    else:
                        print("[エラー] チーできない状態 or チー候補なし")

                elif action == "カン":
                    # カンできるかどうかをチェック
                    if state.game.can_kan and state.game.kan_candidates:
                        if len(state.game.kan_candidates) == 1:
                            kan_tile = state.game.kan_candidates[0]
                            kan_type = state.game.determine_kan_type(0, kan_tile)
                            print(f"[処理] カンを実行します。タイプ: {kan_type}, 牌: {kan_tile}")
                            state.game.process_kan(0, kan_tile, state, kan_type)
                            state.transition_to(PLAYER_DISCARD_PHASE)
                        else:
                            # 複数のカン候補がある場合はUI実装などが必要
                            print("[情報] 複数のカン候補があるため、別のUIで選択が必要です。")
                    else:
                        print("[エラー] カンできない状態 or カン候補なし")

                elif action == "スキップ":
                    print("[スキップ] アクションを行わず次に進みます。")
                    # アクションをスキップして捨て牌フェーズに遷移
                    print("[処理] アクション完了 → プレイヤーの捨て牌フェーズへ移行")
                    state.ai_action_time = current_time + AI_ACTION_DELAY
                    state.transition_to(PLAYER_DISCARD_PHASE)
        return  # `selected_tile` を返さない

    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        # ---- スペースキーでアクションをスキップし、捨て牌フェーズへ ----
        print("[スペースキー] アクションをスキップして捨て牌フェーズへ移行します")

        # アクションをスキップし、プレイヤーの捨て牌フェーズに遷移
        state.ai_action_time = current_time + AI_ACTION_DELAY
        state.transition_to(PLAYER_DISCARD_PHASE)


def handle_pon_wait_phase(state, current_time):
    """
    ポン待機フェーズの処理
    """
    if state.pon_exec_flg:
        print("ポン実行")
        state.game.process_pon(0, state)
        state.pon_exec_flg = False
        state.transition_to(PLAYER_DISCARD_PHASE)
    elif state.skip_flg:
        print("ポンをスキップ")
        state.skip_flg = False
        state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズへ

def is_pon_button_clicked(mouse_pos, pon_button_rect):
    """
    ポンボタンがクリックされたかどうかを判定する。
    """
    return pon_button_rect is not None and pon_button_rect.collidepoint(mouse_pos)

def handle_chi_wait_phase(state, current_time):
    """
    チー待機フェーズの処理
    """
    if state.chi_exec_flg:
        print("チー実行")
        chosen_sequence = state.game.chi_candidates[0]  # 最初の候補を採用（選択式に拡張可能）
        state.game.process_chi(0, chosen_sequence, state)
        state.chi_exec_flg = False
        state.transition_to(PLAYER_DISCARD_PHASE)
    elif state.skip_flg:
        print("チーをスキップ")
        state.skip_flg = False
        state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズへ


def is_chi_button_clicked(mouse_pos, chi_button_rect):
    """
    チーボタンがクリックされたかどうかを判定する。
    """
    return chi_button_rect is not None and chi_button_rect.collidepoint(mouse_pos)

def handle_kan_wait_phase(state, current_time):
    """
    カン待機フェーズの処理
    """
    if state.kan_exec_flg:
        print("カン実行")
        kan_candidates = state.game.kan_candidates
        if kan_candidates:
            state.game.process_kan(0, kan_candidates[0], state, '暗槓')
        state.kan_exec_flg = False
        state.transition_to(PLAYER_DISCARD_PHASE)
    elif state.skip_flg:
        print("カンをスキップ")
        state.skip_flg = False
        state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズへ
