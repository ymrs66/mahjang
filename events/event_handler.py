import pygame
from events.events import handle_player_input
from core.constants import AI_ACTION_DELAY
from drawing.ui_drawing import draw_pon_button, draw_chi_button

def handle_events(state, current_time, screen):
    """
    イベントを処理してゲーム状態を更新する。
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # プレイヤーのチー待機フェーズ中
        if state.game.current_turn == 3:  # 3をチー待機状態として使用
            handle_chi_phase(event, state, screen)
            return True  # 他の処理をスキップして次のフレームへ

        # プレイヤーのポン待機フェーズ中
        if state.game.current_turn == 4:  # 4をポン待機状態として使用
            handle_pon_phase(event, state, screen)
            return True  # 他の処理をスキップして次のフレームへ

        # プレイヤーの通常ターン
        if state.game.current_turn == 0:
            state.tsumo_tile, state.selected_tile = handle_player_input(
                event, state.game, state.tsumo_tile, state.selected_tile, current_time
            )
            if state.game.current_turn == 1:  # AIのターンに移行
                state.ai_action_time = current_time + AI_ACTION_DELAY

        # チーの候補がある場合にボタンを表示
        if state.game.current_turn == 1 and state.game.can_chi:
            if state.game.chi_candidates:
                print(f"チーボタンを表示: {state.game.chi_candidates}")
                state.chi_button_rect = draw_chi_button(screen, True)  # チーボタンの描画関数
            else:
                print("チー候補がありません。ボタンを表示しません。")

        # ポンの候補がある場合にボタンを表示
        if state.game.current_turn == 1 and state.game.can_pon:
            if state.game.pon_candidates:
                print(f"ポンボタンを表示: {state.game.pon_candidates}")
                state.pon_button_rect = draw_pon_button(screen, True)  # ポンボタンの描画関数
            else:
                print("ポン候補がありません。ボタンを表示しません。")

    return True

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
            state.game.process_pon(0)  # ポンの処理を実行
            state.game.can_pon = False

            # ポン後にプレイヤーが捨てるフェーズへ移行
            state.game.current_turn = 0  # プレイヤーのターン
            state.pon_button_rect = None

        # ポンをスキップする場合（スペースキー）
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("ポンをスキップしました")
            state.game.can_pon = False
            state.game.current_turn = 2  # ツモフェーズに移行
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
            state.game.process_chi(0, chosen_sequence)  # チーの処理を実行
            state.game.can_chi = False
            state.chi_button_rect = None
            state.game.current_turn = 0  # プレイヤーターンに移行
            return  # チー待機フェーズ終了

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("チーをスキップしました")
            state.game.can_chi = False
            state.chi_button_rect = None
            state.game.current_turn = 2  # ツモフェーズに移行
        state.draw_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY

def is_chi_button_clicked(mouse_pos, chi_button_rect):
    """
    チーボタンがクリックされたかどうかを判定する。
    """
    return chi_button_rect is not None and chi_button_rect.collidepoint(mouse_pos)
