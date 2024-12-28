##game_state.py
class GameState:
    """
    ゲーム全体の状態を管理するクラス
    """
    def __init__(self):
        self.game = None  # Gameオブジェクト
        self.tsumo_tile = None  # 現在のツモ牌
        self.selected_tile = None  # 現在選択されている牌
        self.ai_action_time = 0  # AIが次に動作する時間
        self.draw_action_time = 0  # プレイヤーがツモるフェーズの時間

    def initialize(self, game):
        self.game = game
        self.tsumo_tile = game.draw_tile(0)  # プレイヤーが最初にツモ