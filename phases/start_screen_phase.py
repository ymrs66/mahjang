# mahjang/phases/start_screen_phase.py
import pygame
from phases.base_phase import BasePhase
from core.constants import PLAYER_DRAW_PHASE, END_SCREEN_PHASE, DEFAULT_FONT_PATH
from core.resource_utils import get_resource_path


class StartScreenPhase(BasePhase):
    def __init__(self, game, state):
        super().__init__(game, state)
        self.start_button_rect = pygame.Rect(400, 300, 200, 50)
        self.quit_button_rect  = pygame.Rect(400, 400, 200, 50)

    def update(self, current_time):
        pass

    def handle_event(self, event):
        import sys
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.start_button_rect.collidepoint(pos):
                print("[TitleScreenPhase] 'Start' button clicked → PLAYER_DRAW_PHASEへ")
                self.state.transition_to(PLAYER_DRAW_PHASE)

            elif self.quit_button_rect.collidepoint(pos):
                print("[TitleScreenPhase] 'Quit' button clicked → 終了")
                self.state.current_phase = END_SCREEN_PHASE
                self.state.transition_to(END_SCREEN_PHASE)

    def render(self, screen):
        # 背景
        screen.fill((0, 100, 200))

        # --- フォント読み込み（日本語対応） --------------------------
        font_path = get_resource_path(DEFAULT_FONT_PATH)
        if font_path:
            title_font  = pygame.font.Font(font_path, 80)
            button_font = pygame.font.Font(font_path, 48)
        else:  # フォントが見つからなければシステムのメイリオを試す
            title_font  = pygame.font.SysFont("Meiryo", 80)
            button_font = pygame.font.SysFont("Meiryo", 48)

        # タイトル
        title_surface = title_font.render("麻雀ゲーム", True, (255, 255, 255))
        screen.blit(title_surface, (300, 150))

        # ボタン
        pygame.draw.rect(screen, (0, 255, 0), self.start_button_rect)
        pygame.draw.rect(screen, (255, 0, 0),  self.quit_button_rect)

        start_text = button_font.render("START", True, (0, 0, 0))
        quit_text  = button_font.render("QUIT",  True, (0, 0, 0))
        screen.blit(start_text, (self.start_button_rect.x + 30, self.start_button_rect.y + 5))
        screen.blit(quit_text,  (self.quit_button_rect.x  + 40, self.quit_button_rect.y  + 5))
