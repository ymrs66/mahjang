# File: core/event_dispatcher.py
import pygame

class EventDispatcher:
    def __init__(self, game_state):
        self.game_state = game_state

    def dispatch(self, event):
        # 例：共通処理（F1でヘルプ表示、ESCで終了など）
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                print("[EventDispatcher] ヘルプ表示")
            elif event.key == pygame.K_ESCAPE:
                print("[EventDispatcher] ESCが押された → ゲーム終了要求")
                # 必要に応じてゲーム終了フラグを設定する
        # 現在のフェーズオブジェクトにイベントを渡す
        if self.game_state.current_phase_object:
            self.game_state.current_phase_object.handle_event(event)
