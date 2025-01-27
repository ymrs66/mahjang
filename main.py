##main.py
import pygame
from core.game import Game
from core.game_state import GameState
from core.constants import (
    PLAYER_DISCARD_PHASE,
    PLAYER_DRAW_PHASE,
    AI_DRAW_PHASE,
    AI_DISCARD_PHASE,
    CHI_WAIT_PHASE,
    PON_WAIT_PHASE,
    KAN_WAIT_PHASE,
    AI_ACTION_SELECTION_PHASE,
    PLAYER_ACTION_SELECTION_PHASE,
    GAME_END_PHASE
)

from events.event_handler import handle_events  # イベント処理を外部モジュールに分離
from core.game_logic import (
    handle_ai_draw_phase,
    handle_ai_discard_phase,
    handle_ai_action_selection_phase,
    handle_player_draw_phase,
    handle_player_discard_phase,
    handle_player_action_selection_phase,
    handle_pon_wait_phase,
    handle_chi_wait_phase,
    handle_kan_wait_phase
)
# 描画関連
from drawing.player_drawing import draw_player_state # プレイヤーの手牌・ポン・チーを描画
from drawing.ai_drawing import draw_ai_tiles
from drawing.discard_drawing import draw_discards
from drawing.ui_drawing import draw_action_buttons
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Pygame初期設定
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("麻雀ゲーム")
clock = pygame.time.Clock()

# メインループ
def main_loop():
    """
    ゲームのメインループ
    """
    game = Game()
    game.shuffle_wall()
    game.deal_initial_hand()

    state = GameState()
    state.initialize(game)

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # 1. **イベント処理** （ここでマウスやキーボードの入力を拾う）
        if not handle_events(state, current_time, screen):
            running = False
            break

        # 2. フェーズ分岐してゲームロジックを呼ぶ
        if state.current_phase == AI_DRAW_PHASE:  # AIのツモフェーズ
            handle_ai_draw_phase(state, current_time)
        elif state.current_phase == AI_DISCARD_PHASE:  # AIの捨て牌フェーズ
            handle_ai_discard_phase(state, current_time)
        elif state.current_phase == AI_ACTION_SELECTION_PHASE:  # AIのアクション選択フェーズ
            handle_ai_action_selection_phase(state, current_time)
        elif state.current_phase == PLAYER_DRAW_PHASE:  # プレイヤーのツモフェーズ
            handle_player_draw_phase(state, current_time)
        elif state.current_phase == PLAYER_DISCARD_PHASE:  # プレイヤーの捨て牌フェーズ
            handle_player_discard_phase(state, current_time)
        elif state.current_phase == PLAYER_ACTION_SELECTION_PHASE:  # プレイヤーのアクション選択フェーズ
            handle_player_action_selection_phase(state, current_time)
        elif state.current_phase == PON_WAIT_PHASE:  # ポン待機フェーズ
            handle_pon_wait_phase(state, current_time)
        elif state.current_phase == CHI_WAIT_PHASE:  # チー待機フェーズ
            handle_chi_wait_phase(state, current_time)
        elif state.current_phase == KAN_WAIT_PHASE:  # カン待機フェーズ
            handle_kan_wait_phase(state, current_time)
        elif state.current_phase == GAME_END_PHASE:  # ゲーム終了フェーズ
            print("[ゲーム終了] ゲームが終了しました")
            running = False
        else:
            print(f"[警告] 未知のフェーズ: {state.current_phase} (想定外の状態)")
            running = False

        # 描画処理
        render_game(state)

        # フレームレート制御
        clock.tick(30)

    pygame.quit()

# 描画処理
def render_game(state):
    """
    画面描画を管理する
    """
    screen.fill((0, 128, 0))  # 背景色
    draw_player_state(screen, state.game.players[0], state.selected_tile)  # プレイヤーの手牌・ポン・チーを描画
    draw_ai_tiles(screen)
    draw_discards(screen, state.game.discards)

    if state.current_phase == PLAYER_ACTION_SELECTION_PHASE and state.available_actions:
        # 毎フレーム、行動ボタンを描画して Rect を更新
        state.action_buttons = draw_action_buttons(screen, state.available_actions)    
    pygame.display.flip()
    
if __name__ == "__main__":
    main_loop()