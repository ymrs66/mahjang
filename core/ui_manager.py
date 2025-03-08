# File: core/ui_manager.py
import pygame
from drawing.renderer import render_game_state
from core.event_dispatcher import EventDispatcher

class UIManager:
    def __init__(self, screen, game_state):
        self.screen = screen
        self.game_state = game_state
        self.dispatcher = EventDispatcher(game_state)

    def process_events(self):
        """Pygame のイベントを処理し、現在のフェーズにディスパッチする"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            self.dispatcher.dispatch(event)
        return True

    def update(self, current_time):
        """現在のフェーズの update() を呼び出す"""
        if self.game_state.current_phase_object:
            self.game_state.current_phase_object.update(current_time)

    def render(self):
        """ゲーム状態に応じた描画を実行する"""
        render_game_state(self.game_state, self.screen)
