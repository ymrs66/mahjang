##game_state.py
class GameState:
    """
    ゲーム全体の状態を管理するクラス
    """
    def __init__(self):
        self.game = None
        self.tsumo_tile = None
        self.selected_tile = None
        self.ai_action_time = 0
        self.draw_action_time = 0
        self.chi_button_rect = None  # チーボタンの位置とサイズ
        self.pon_button_rect = None  # ポンボタンの位置とサイズ

    def initialize(self, game):
        self.game = game
        self.tsumo_tile = game.draw_tile(0)
        self.selected_tile = None
        self.ai_action_time = 0
        self.draw_action_time = 0
        self.chi_button_rect = None
        self.pon_button_rect = None