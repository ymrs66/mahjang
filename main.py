##main.py
import pygame
from core.game import Game
from core.game_state import GameState
from events.event_handler import handle_events  # イベント処理を外部モジュールに分離
from core.game_logic import handle_ai_turn, handle_draw_phase  # ゲームロジックを外部モジュールに分離
# 描画関連
from drawing.player_drawing import draw_tiles, draw_player_state # プレイヤーの手牌・ポン・チーを描画
from drawing.ai_drawing import draw_ai_tiles
from drawing.discard_drawing import draw_discards
from drawing.ui_drawing import draw_pon_button, draw_chi_button
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
    # ゲームと状態の初期化
    game = Game()
    game.shuffle_wall()
    game.deal_initial_hand()

    state = GameState()
    state.initialize(game)  # `chi_button_rect` も初期化される

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # イベント処理
        running = handle_events(state, current_time, screen)

        # ゲーム終了判定
        if state.game.is_game_over():
            print("ゲーム終了！")
            break

        # ターン進行処理
        if state.game.current_turn == 1:  # AIのターン
            handle_ai_turn(state, current_time)
        elif state.game.current_turn == 2:  # ツモフェーズ
            handle_draw_phase(state, current_time)

        # 描画
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
    
    # ポンボタンが必要なら描画
    if state.game.can_pon:
        draw_pon_button(screen, True)
    
    # チーボタンが必要なら描画
    if state.game.can_chi:
        state.chi_button_rect = draw_chi_button(screen, True)
    
    pygame.display.flip()
    
if __name__ == "__main__":
    main_loop()