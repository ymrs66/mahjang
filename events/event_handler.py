# File: mahjang\events\event_handler.py

import pygame
from events.events import handle_player_input
from core.constants import *  # 全ての定義をインポート
from drawing.ui_drawing import draw_pon_button, draw_chi_button, draw_kan_button

def handle_events(state, current_time, screen):
    print(f"[デバッグ] 現在のフェーズ: {state.current_phase}")

    for event in pygame.event.get():
        print(f"[デバッグ] イベント取得: {event}")

        if event.type == pygame.QUIT:
            print("[処理] ゲーム終了")
            return False

        # --- ① プレイヤーの手牌クリック関連 ---
        if state.current_phase in [PLAYER_DISCARD_PHASE, PLAYER_DRAW_PHASE]:
            # AIの待ち時間中であれば、プレイヤー操作を無視
            if current_time < state.ai_action_time:
                continue

            # プレイヤーのクリック・キー入力を処理
            selected_tile = handle_player_input(
                event,
                state.game,
                state.selected_tile,
                current_time,
                state,
                screen
            )
            state.selected_tile = selected_tile

        # --- ② ACTION_SELECTION_PHASE 用に handle_action_selection を呼ぶ ---
        if state.current_phase == PLAYER_ACTION_SELECTION_PHASE:
            handle_action_selection(event, state, current_time)

        # --- ③ ポン・チー・カン待機フェーズのボタン処理 ---
        if state.current_phase == MELD_WAIT_PHASE:
            if event.type == pygame.MOUSEBUTTONDOWN:
            # 例: ponボタン・chiボタン・kanボタンそれぞれのRectをチェック
            #     - クリックされたら state.meld_action = 'pon' / 'chi' / 'kan' にする
            #     - スペースキーなら 'skip'
                print("マウス押下")
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                print("スキップ処理（スペースキー）")
                state.meld_action = "skip"

    return True

def handle_action_selection(event, state, current_time):
    """
    アクション選択フェーズ(PLAYER_ACTION_SELECTION_PHASE)で、
    表示中のボタンをクリックしてどれを実行するかを決定する。
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        # 各アクション（"ポン", "チー", "カン", "スキップ"など）のボタン領域を判定
        for action, rect in state.action_buttons.items():
            if rect.collidepoint(event.pos):
                print(f"[クリックされたアクション]: {action}")

                if action == "ポン":
                    # meld_enabled["pon"] と meld_candidates["pon"] をチェック
                    print(f'[デバッグ] meld_enabled["pon"]={state.game.meld_manager.meld_enabled["pon"]}, '
                          f'meld_candidates["pon"]={state.game.meld_manager.meld_candidates["pon"]}')
                    if state.game.meld_manager.meld_enabled["pon"] and state.game.meld_manager.meld_candidates["pon"]:
                        state.game.meld_manager.process_pon(0, state)
                        state.transition_to(PLAYER_DISCARD_PHASE)
                    else:
                        print("[エラー] ポンできない状態なのにボタンが押されました。")

                elif action == "チー":
                    # meld_enabled["chi"] と meld_candidates["chi"] をチェック
                    if state.game.meld_manager.meld_enabled["chi"] and state.game.meld_manager.meld_candidates["chi"]:
                        chosen_sequence = state.game.meld_manager.meld_candidates["chi"][0]
                        state.game.meld_manager.process_chi(0, chosen_sequence, state)
                        state.transition_to(PLAYER_DISCARD_PHASE)
                    else:
                        print("[エラー] チーできない状態 or チー候補なし")

                elif action == "カン":
                    # meld_enabled["kan"] と meld_candidates["kan"] をチェック
                    if state.game.meld_manager.meld_enabled["kan"] and state.game.meld_manager.meld_candidates["kan"]:
                        if len(state.game.meld_manager.meld_candidates["kan"]) == 1:
                            kan_tile = state.game.meld_manager.meld_candidates["kan"][0]
                            kan_type = state.game.determine_kan_type(0, kan_tile)
                            state.game.meld_manager.process_kan(0, kan_tile, state)
                            state.transition_to(PLAYER_DISCARD_PHASE)
                        else:
                            print("[情報] 複数のカン候補があるため、別のUIで選択が必要です。")
                    else:
                        print("[エラー] カンできない状態 or カン候補なし")
                elif action == "ツモ":
                    print("[処理] ツモを実行します")
                    # ツモ処理を呼び出す
                    state.game.process_tsumo(0,state)
                    return  # 押下処理を終えて抜ける

                elif action == "ロン":
                    print("[処理] ロンを実行します")
                    discard_tile = state.game.target_tile
                    state.game.process_ron(0, discard_tile, state)

                elif action == "スキップ":
                    print("[スキップ] アクションを行わず次に進みます。")
                    state.ai_action_time = current_time + AI_ACTION_DELAY
                    state.transition_to(PLAYER_DISCARD_PHASE)

        return  # 選択処理が終わったらここで抜ける

    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
    # ★もし "ツモ" がアクション一覧に含まれている場合はスキップさせない
        if "ツモ" in state.available_actions:
            print("[情報] ツモ可能なため、スペースキーではスキップできません。")
            # 何もせず return するので「ツモボタン」を押すしかない
            return
        else:
            print("[スペースキー] アクションをスキップしてツモフェーズへ移行します")
            state.ai_action_time = current_time + AI_ACTION_DELAY
            state.transition_to(PLAYER_DRAW_PHASE)

# 以下はポン待機フェーズ等がまだ残っている場合のサンプル。
# 実際には handle_meld_wait_phase(...) に統合するのが望ましい。

def handle_meld_wait_phase(state, current_time):
    """
    ポン・チー・カン待機フェーズを一本化。
    state.meld_action が 'pon','chi','kan','skip' のどれなのかを見て処理。
    """
    print("[待機フェーズ] ポン or チー or カン いずれかを待機中...")

    if state.meld_action == "skip":
        # スキップ処理
        print("[スキップ] メルドを行わずツモへ")
        state.meld_action = None
        state.transition_to(PLAYER_DRAW_PHASE)
        return

    elif state.meld_action == "pon":
        print("[待機] ポン実行フラグを検知")
        state.game.process_pon(0, state)
        state.meld_action = None

    elif state.meld_action == "chi":
        print("[待機] チー実行フラグを検知")
        # 例: 複数候補がある場合は state.game.meld_candidates["chi"] から選ぶ
        # ここでは先頭を選ぶとして:
        chi_candidates = state.game.meld_candidates["chi"]
        if chi_candidates:
            chosen_sequence = chi_candidates[0]
            state.game.process_chi(0, chosen_sequence, state)
        else:
            print("[エラー] chi候補がありません")
        state.meld_action = None

    elif state.meld_action == "kan":
        print("[待機] カン実行フラグを検知")
        kan_candidates = state.game.meld_candidates["kan"]
        if kan_candidates:
            kan_tile = kan_candidates[0]
            state.game.process_kan(0, kan_tile, state)
        else:
            print("[エラー] kan候補がありません")
        state.meld_action = None