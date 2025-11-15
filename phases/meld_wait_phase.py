# phases/meld_wait_phase.py
from .base_phase import BasePhase
from core.constants import (
    PLAYER_DRAW_PHASE,
    MELD_WAIT_PHASE
)

class MeldWaitPhase(BasePhase):
    """
    もともと handle_meld_wait_phase(state, current_time) の内容をクラス化。
    ポン／チー／カンの待機フェーズを処理。
    """

    def update(self, current_time):
        print("[MeldWaitPhase] update")
        # 直近の他家捨て牌（2人戦想定：AI=1）
        discard_tile = self.state.game.discards[1][-1] if self.state.game.discards[1] else None

        if self.state.meld_action == "skip":
            print("[MeldWaitPhase] skip → PLAYER_DRAW_PHASE")
            self.state.meld_action = None
            self.state.transition_to(PLAYER_DRAW_PHASE)
            return
        elif self.state.meld_action == "pon":
            print("[MeldWaitPhase] ポン実行")
            self.state.game.meld_manager.process_pon(0, discard_tile, self.state)
            self.state.meld_action = None
        elif self.state.meld_action == "chi":
            print("[MeldWaitPhase] チー実行")
            chi_candidates = self.state.game.meld_manager.meld_candidates["chi"]
            if chi_candidates:
                self.state.game.meld_manager.process_chi(0, discard_tile, chi_candidates[0], self.state)
            self.state.meld_action = None
        elif self.state.meld_action == "kan":
            print("[MeldWaitPhase] カン実行")
            kan_candidates = self.state.game.meld_manager.meld_candidates["kan"]
            if kan_candidates:
                self.state.game.meld_manager.process_kan(0, discard_tile, kan_candidates[0], self.state)
            self.state.meld_action = None

        # どの道、メルド後は捨て牌 or 次のフェーズへ進む想定
        # (適宜、PLAYER_DISCARD_PHASEへ移行するなど)

    def handle_event(self, event):
        """
        スペースキーによるスキップなどを拾う場合:
        """
        # まず共通処理を実行
        import pygame
        super().handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("[MeldWaitPhase] meld_action='skip'")
            self.state.meld_action = "skip"
