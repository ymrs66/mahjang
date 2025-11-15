# File: mahjang/phases/end_screen_phase.py

import pygame
from phases.base_phase import BasePhase
from core.constants import GAME_END_PHASE,END_SCREEN_PHASE

class EndScreenPhase(BasePhase):
    def __init__(self, game, state):
        super().__init__(game, state)
        self.exit_button_rect = pygame.Rect(400, 400, 200, 50)

    def update(self, current_time):
        """
        ゲーム終了画面でのタイマー処理やアニメーション。なければpass。
        """
        self.state.transition_to(END_SCREEN_PHASE)

    def handle_event(self, event):
        import sys
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.exit_button_rect.collidepoint(pos):
                print("[EndScreenPhase] Exit button clicked → メインループ終了")
                # 例: ここでは GameState.current_phase を GAME_END_PHASE にして、
                # main_loop で running=False にする
                self.state.current_phase = GAME_END_PHASE

    def render(self, screen):
        """
        終了画面の描画。
        """
        screen.fill((100, 100, 100))  # グレー背景
        font = pygame.font.Font(None, 60)
        msg_surface = font.render("Game Over", True, (255, 255, 255))
        screen.blit(msg_surface, (350, 200))

        # Exitボタン
        pygame.draw.rect(screen, (200, 200, 200), self.exit_button_rect)
        exit_text = font.render("EXIT", True, (0, 0, 0))
        screen.blit(exit_text, (self.exit_button_rect.x + 40, self.exit_button_rect.y + 5))
