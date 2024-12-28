##event_handler.py
import pygame
from events.events import handle_player_input, handle_pon_click
from core.constants import AI_ACTION_DELAY
from drawing.ui_drawing import draw_pon_button

def handle_events(state, current_time, screen):
    """
    イベントを処理してゲーム状態を更新する。
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # プレイヤーのターン
        if state.game.current_turn == 0:
            state.tsumo_tile, state.selected_tile = handle_player_input(
                event, state.game, state.tsumo_tile, state.selected_tile, current_time
            )
            if state.game.current_turn == 1:  # プレイヤーが牌を捨て終わりAIのターンに移行
                state.ai_action_time = current_time + AI_ACTION_DELAY

        # ポン待機フェーズ
        if state.game.current_turn == 3:
            handle_pon_phase(event, state, screen)

    return True

def handle_pon_phase(event, state, screen):
    """
    ポンが可能な状態での操作。
    """
    if state.game.can_pon:
        pon_button_rect = draw_pon_button(screen, True)
        if handle_pon_click(event, pon_button_rect, state.game):  # ポンボタンがクリックされた場合
            print(f"ポンを実行: {state.game.target_tile}")
            state.game.process_pon(0)  # ポンの処理を実行
            state.game.can_pon = False
            state.game.current_turn = 2  # ツモフェーズに移行
            state.draw_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # スペースキーでスキップ
            print("ポンをスキップしました")
            state.game.can_pon = False
            state.game.current_turn = 2  # ツモフェーズに移行
            state.draw_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY