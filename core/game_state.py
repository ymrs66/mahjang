# File: mahjang/core/game_state.py
from core.constants import (
    PLAYER_DISCARD_PHASE,
    PLAYER_DRAW_PHASE,
    AI_DRAW_PHASE,
    AI_DISCARD_PHASE,
    MELD_WAIT_PHASE,
    AI_ACTION_SELECTION_PHASE,
    PLAYER_ACTION_SELECTION_PHASE,
    PLAYER_SELECT_TILE_PHASE,
    WIN_RESULT_PHASE,
    GAME_END_PHASE,
    START_SCREEN_PHASE,
    END_SCREEN_PHASE,
)
from phases.draw_phase import PlayerDrawPhase, AIDrawPhase
from phases.discard_phase import PlayerDiscardPhase, AIDiscardPhase
from phases.select_tile_phase import PlayerSelectTilePhase
from phases.player_action_selection_phase import PlayerActionSelectionPhase
from phases.ai_action_selection_phase import AIActionSelectionPhase
from phases.meld_wait_phase import MeldWaitPhase
from phases.win_result_phase import WinResultPhase
from phases.start_screen_phase import StartScreenPhase
from phases.end_screen_phase import EndScreenPhase

# フェーズIDとクラスの対応表
PHASE_CLASS_MAP = {
    PLAYER_DRAW_PHASE: PlayerDrawPhase,
    PLAYER_DISCARD_PHASE: PlayerDiscardPhase,
    AI_DRAW_PHASE: AIDrawPhase,
    AI_DISCARD_PHASE: AIDiscardPhase,
    PLAYER_ACTION_SELECTION_PHASE: PlayerActionSelectionPhase,
    AI_ACTION_SELECTION_PHASE: AIActionSelectionPhase,
    MELD_WAIT_PHASE: MeldWaitPhase,
    PLAYER_SELECT_TILE_PHASE: PlayerSelectTilePhase,
    WIN_RESULT_PHASE: WinResultPhase,
    START_SCREEN_PHASE: StartScreenPhase,
    END_SCREEN_PHASE: EndScreenPhase,
}

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
        self.current_phase = START_SCREEN_PHASE
        self.current_phase_object = None  #現在のフェーズのオブジェクト
        self.action_buttons = {}
        self.available_actions = []
        self.waiting_for_player_discard = False
        self.meld_action = None   # "pon", "chi", "kan", "skip", または None
        self.drawn_tile = None

        self.chi_button_rect = None
        self.pon_button_rect = None
        self.kan_button_rect = None

    def initialize(self, game):
        self.__init__()  # 属性をリセット
        self.game = game
        # 初期フェーズのオブジェクトを生成
        self.set_current_phase_object(self.current_phase)

    def set_current_phase_object(self, phase_id):
        """フェーズIDに対応するフェーズオブジェクトを生成して保持する"""
        phase_class = PHASE_CLASS_MAP.get(phase_id)
        if phase_class:
            self.current_phase_object = phase_class(self.game, self)
        else:
            self.current_phase_object = None
            print(f"[警告] 未対応のフェーズID: {phase_id}")

    def transition_to(self, new_phase):
        print(f"フェーズ遷移: {self.current_phase} -> {new_phase}")
        self.phase_history.append(self.current_phase)
        self.current_phase = new_phase
        # 新しいフェーズオブジェクトを生成して保持
        self.set_current_phase_object(new_phase)

    def revert_to_previous_phase(self):
        if self.phase_history:
            self.current_phase = self.phase_history.pop()
            self.set_current_phase_object(self.current_phase)
            print(f"フェーズを前に戻す: {self.current_phase}")
        else:
            print("フェーズ履歴がありません。")
