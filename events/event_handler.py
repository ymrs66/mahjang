##event_handler.py
import pygame
from events.events import handle_player_input, handle_pon_click
from core.constants import AI_ACTION_DELAY
from drawing.ui_drawing import draw_pon_button, draw_chi_button

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
            if state.game.current_turn == 1:
                state.ai_action_time = current_time + AI_ACTION_DELAY

        # チー待機フェーズ
        if state.game.can_chi and state.game.current_turn == 3:
            print("チー待機フェーズに移行")
            handle_chi_phase(event, state, screen)
            pygame.event.clear()  # イベントをクリアして無限ループを防ぐ

    return True


def handle_pon_phase(event, state, screen):
    """
    ポンが可能な状態での操作。
    """
    if state.game.can_pon:
        pon_button_rect = draw_pon_button(screen, True)
        if event.type == pygame.MOUSEBUTTONDOWN and pon_button_rect.collidepoint(event.pos):  # ポンボタンがクリックされた場合
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

def handle_chi_phase(event, state, screen):
    """
    チー待機フェーズの処理。
    """
    if state.game.can_chi:
        print("チー待機フェーズ処理中")
        
        # ボタンがまだ描画されていない場合、新しく描画
        if not state.chi_button_rect:
            state.chi_button_rect = draw_chi_button(screen, True)
        
        pygame.display.update()  # 画面を更新

        # チーボタンがクリックされた場合
        if event.type == pygame.MOUSEBUTTONDOWN and state.chi_button_rect.collidepoint(event.pos):
            print("チーを実行")
            # 適切な順子を選択（暫定的に自動選択）
            chosen_sequence = [
                int(state.game.target_tile.value) - 1,
                int(state.game.target_tile.value) + 1,
            ]
            state.game.process_chi(0, chosen_sequence)
            state.game.can_chi = False
            state.game.current_turn = 0  # プレイヤーのターンに戻る
            state.chi_button_rect = None  # ボタンの状態をリセット

        # スペースキーでスキップ
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("チーをスキップしました")
            state.game.can_chi = False
            state.game.current_turn = 2  # ツモフェーズに移行
            state.chi_button_rect = None  # ボタンの状態をリセット