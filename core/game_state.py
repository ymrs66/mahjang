##game_state.py
from core.constants import PLAYER_DRAW_PHASE
class GameState:
    """
    ゲーム全体の状態を管理するクラス
    """
    def __init__(self):
        self.game = None
        self.selected_tile = None
        self.ai_action_time = 0
        self.draw_action_time = 0
        self.phase_history = []
        self.current_phase = PLAYER_DRAW_PHASE
        self.action_buttons = {}
        self.available_actions = []
        self.waiting_for_player_discard = False

        # ここで "どのメルドを実行したいか" を示すフラグを1つに統合
        self.meld_action = None   # "pon", "chi", "kan", "skip", または None

        # ボタンの位置など既存の変数はそのまま or まとめるかはお好み
        self.chi_button_rect = None
        self.pon_button_rect = None
        self.kan_button_rect = None

    def initialize(self, game):
        """
        ゲームの初期化
        """
        self.__init__()  # 属性をリセット
        self.game = game

    def transition_to(self, new_phase):
        """フェーズを遷移させる"""
        print(f"フェーズ遷移: {self.current_phase} -> {new_phase}")
        self.phase_history.append(self.current_phase)
        self.current_phase = new_phase

    def revert_to_previous_phase(self):
        """前のフェーズに戻す"""
        if self.phase_history:
            self.current_phase = self.phase_history.pop()
            print(f"フェーズを前に戻す: {self.current_phase}")
        else:
            print("フェーズ履歴がありません。")