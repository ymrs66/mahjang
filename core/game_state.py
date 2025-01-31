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
        self.chi_button_rect = None  # チーボタンの位置とサイズ
        self.pon_button_rect = None  # ポンボタンの位置とサイズ
        self.kan_button_rect = None  # カンボタンの位置とサイズ
        self.phase_history = []  # 遷移履歴を保持（デバッグ用）
        self.current_phase = PLAYER_DRAW_PHASE  # 初期フェーズを直接設定
        self.action_buttons = {}  # アクションボタンの矩形情報を保持
        self.available_actions = []  # 利用可能なアクションのリスト
        self.waiting_for_player_discard = False  # ✅ プレイヤーの捨て牌待機状態を追加
        self.pon_exec_flg = False
        self.chi_exec_flg = False
        self.kan_exec_flg = False
        self.skip_flg = False

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