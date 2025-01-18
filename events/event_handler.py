import pygame
from events.events import handle_player_input
from core.constants import *  # 全ての定義をインポート
from drawing.ui_drawing import draw_pon_button, draw_chi_button,draw_kan_button
from core.game_logic import handle_ai_turn

def handle_events(state, current_time, screen):
    """
    イベントを処理してゲーム状態を更新する。
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # **アクション選択フェーズ**
        if state.current_phase == ACTION_SELECTION_PHASE:
            print("[イベント] アクション選択フェーズ")
            handle_action_selection(event, state)

            # **アクションが選択されたかどうかを確認し、フェーズ遷移**
            if not state.available_actions:
                print("[処理] アクションがないためAIターンへ")
                state.transition_to(AI_TURN_PHASE)
            return True  # 次のイベントを待つためにループを終了

        # **プレイヤーの捨て牌フェーズ**
        if state.current_phase == PLAYER_DISCARD_PHASE:
            print("[イベント] プレイヤーの捨て牌フェーズ")
            # プレイヤーの入力を処理
            prev_selected_tile = state.selected_tile  # 変更前の選択状態を保持
            state.tsumo_tile, state.selected_tile = handle_player_input(
                event, state.game, state.tsumo_tile, state.selected_tile, current_time, state, screen
            )

            # **プレイヤーが牌を捨てたか確認**
            if prev_selected_tile != state.selected_tile and state.selected_tile is None:
                print("[確認] プレイヤーが牌を捨てました")

                # 捨て牌後にアクション選択が必要かチェック
                discard_tile = state.game.discards[0][-1] if state.game.discards[0] else None
                if discard_tile:
                    actions = state.game.get_available_actions(0, discard_tile)
                    print(f"[アクション候補] {actions}")

                    if actions:
                        state.available_actions = actions
                        state.action_buttons = draw_action_buttons(screen, actions)
                        state.transition_to(ACTION_SELECTION_PHASE)  # **アクション選択フェーズ**
                        return True

                # **AIターンに移行する際にディレイを設定**
                state.ai_action_time = current_time + AI_ACTION_DELAY
                state.transition_to(AI_TURN_PHASE)
                return True

        # **AIのターン**
        if state.current_phase == AI_TURN_PHASE:
            print("[イベント] AIのターンに移行しました")
            
            # **ディレイ処理**
            if current_time < state.ai_action_time:
                print(f"[待機] AIターン開始まで {state.ai_action_time - current_time} ms")
                return True  # まだディレイ時間が経過していない
            
            handle_ai_turn(state, current_time)  # AIの処理
            return True

        # **ポン・チー・カン待機フェーズ**
        if state.current_phase == CHI_WAIT_PHASE:
            print("[イベント] チー待機フェーズ")
            handle_chi_phase(event, state, screen)
            return True
        if state.current_phase == PON_WAIT_PHASE:
            print("[イベント] ポン待機フェーズ")
            handle_pon_phase(event, state, screen)
            return True
        if state.current_phase == KAN_WAIT_PHASE:
            print("[イベント] カン待機フェーズ")
            handle_kan_phase(event, state, screen)
            return True

    return True

def handle_action_selection(event, state):
    """
    アクション選択フェーズの処理を行う。
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        for action, rect in state.action_buttons.items():
            if rect.collidepoint(event.pos):
                print(f"選択されたアクション: {action}")

                if action == "ポン":
                    state.game.process_pon(0, state)
                elif action == "チー":
                    # チー候補から選択（暫定的に最初の候補を使用）
                    if state.game.chi_candidates:
                        chosen_sequence = state.game.chi_candidates[0]
                        state.game.process_chi(0, chosen_sequence, state)
                elif action == "カン":
                    # 複数のカン候補がある場合、プレイヤーに選択させる
                    kan_candidates = state.game.kan_candidates
                    if len(kan_candidates) == 1:
                        kan_tile = kan_candidates[0]
                        kan_type = state.game.determine_kan_type(0, kan_tile)  # カンの種類を判定
                        state.game.process_kan(0, kan_tile, state, kan_type)
                    elif len(kan_candidates) > 1:
                        # 複数のカン候補がある場合、選択用のボタンを表示（別フェーズを追加可能）
                        state.available_kan_choices = kan_candidates
                        state.transition_to(KAN_WAIT_PHASE)
                        return
                
                # **修正点: AIターンに移行する**
                print("[処理] アクション完了 → AIのターンへ移行")
                state.ai_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY  # AIのディレイ設定
                state.transition_to(AI_TURN_PHASE)
                return

def handle_pon_phase(event, state, screen):
    """
    ポンが可能な状態での操作。
    """
    if state.game.can_pon:
        # ポンボタンの描画
        pon_button_rect = draw_pon_button(screen, True)

        # プレイヤーがポンボタンをクリックした場合
        if event.type == pygame.MOUSEBUTTONDOWN and pon_button_rect.collidepoint(event.pos):
            print(f"ポンを実行: {state.game.target_tile}")
            state.game.process_pon(0,state)  # ポンの処理を実行
            state.game.can_pon = False

            # ポン後にプレイヤーが捨てるフェーズへ移行
            state.transition_to(PLAYER_DISCARD_PHASE)  # プレイヤーのターン
            state.pon_button_rect = None

        # ポンをスキップする場合（スペースキー）
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("ポンをスキップしました")
            state.game.can_pon = False
            state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズに移行
            state.pon_button_rect = None
        state.draw_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY

def is_pon_button_clicked(mouse_pos, pon_button_rect):
    """
    ポンボタンがクリックされたかどうかを判定する。
    """
    return pon_button_rect is not None and pon_button_rect.collidepoint(mouse_pos)

def handle_chi_phase(event, state, screen):
    """
    チー待機フェーズの処理。
    """
    if state.game.can_chi:
        print(f"チー待機フェーズ中: 候補={state.game.chi_candidates}")

        if not state.chi_button_rect:
            state.chi_button_rect = draw_chi_button(screen, True)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and state.chi_button_rect.collidepoint(event.pos):
            print("チーを実行")
            chosen_sequence = state.game.chi_candidates[0]  # 暫定的に最初の候補を選択
            state.game.process_chi(0, chosen_sequence,state)  # チーの処理を実行
            state.game.can_chi = False
            state.chi_button_rect = None
            state.transition_to(PLAYER_DISCARD_PHASE)  # プレイヤーターンに移行
            return  # チー待機フェーズ終了

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("チーをスキップしました")
            state.game.can_chi = False
            state.chi_button_rect = None
            state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズに移行
        state.draw_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY

def is_chi_button_clicked(mouse_pos, chi_button_rect):
    """
    チーボタンがクリックされたかどうかを判定する。
    """
    return chi_button_rect is not None and chi_button_rect.collidepoint(mouse_pos)

def handle_kan_phase(event, state, screen):
    """
    カン待機フェーズの処理。
    """
    if state.game.can_kan:
        kan_button_rect = draw_kan_button(screen, True)  # カンボタンの描画
        pygame.display.update()

        # カンボタンがクリックされた場合
        if event.type == pygame.MOUSEBUTTONDOWN and kan_button_rect.collidepoint(event.pos):
            print("カンを実行")
            kan_candidates = state.game.check_kan(0)  # プレイヤーIDは0
            if kan_candidates:
                # 暗槓を例として実行（ユーザー選択を拡張可能）
                state.game.process_kan(0, kan_candidates[0], state,'暗槓')
            state.game.can_kan = False
            state.kan_button_rect = None
            state.transition_to(PLAYER_DISCARD_PHASE)   # プレイヤーのターンに戻る
            return

        # スペースキーでカンをスキップする場合
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("カンをスキップしました")
            state.game.can_kan = False
            state.kan_button_rect = None
            state.transition_to(PLAYER_DRAW_PHASE)  # ツモフェーズに移行
            return