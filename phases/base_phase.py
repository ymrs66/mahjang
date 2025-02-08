# phases/base_phase.py
class BasePhase:
    def __init__(self, game, state):
        self.game = game
        self.state = state

    def handle_event(self, event):
        """イベントを処理する"""
        pass

    def update(self, current_time):
        """フェーズの更新処理"""
        pass

    def render(self, screen):
        """描画処理"""
        pass