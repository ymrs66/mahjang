# File: mahjang/main.py
import pygame
from core.game import Game
from core.game_state import GameState
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GAME_END_PHASE
from core.ui_manager import UIManager  # 新たに追加

# Pygame 初期設定
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("麻雀ゲーム")
clock = pygame.time.Clock()

def main_loop():
    # ゲーム初期化
    game = Game()
    game.shuffle_wall()
    game.deal_initial_hand()

    state = GameState()
    state.initialize(game)  # この時点で current_phase_object が生成される

    # UIManager の作成
    ui_manager = UIManager(screen, state)

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # イベント処理
        running = ui_manager.process_events()
        if not running:
            break

        # ゲーム状態の更新
        if state.current_phase == GAME_END_PHASE:
            print("[ゲーム終了] ゲームが終了しました")
            running = False
        else:
            ui_manager.update(current_time)

        # 描画
        ui_manager.render()

        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    main_loop()
