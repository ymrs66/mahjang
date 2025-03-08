# phases/ai_action_selection_phase.py
from .base_phase import BasePhase
from core.constants import (
    PLAYER_DRAW_PHASE,
    AI_DRAW_PHASE,
    AI_ACTION_SELECTION_PHASE,
    AI_ACTION_DELAY
)

class AIActionSelectionPhase(BasePhase):
    """
    元の handle_ai_action_selection_phase(state, current_time)
    の内容を移行してクラス化。
    """

    def update(self, current_time):
        print("[AIActionSelectionPhase] update")

        # 1) プレイヤーの捨て牌が無ければスキップ
        if not self.state.game.discards[0]:
            print("[AIActionSelectionPhase] プレイヤーの捨て牌なし → PLAYER_DRAW_PHASEへ")
            self.state.transition_to(PLAYER_DRAW_PHASE)
            return

        # 2) 直近のプレイヤー捨て牌を取得
        discard_tile = self.state.game.discards[0][-1]

        # 3) AIのアクション候補を取得
        actions = self.state.game.get_available_actions(player_id=1, discard_tile=discard_tile)
        print(f"[AIActionSelectionPhase] AI行動候補: {actions}")

        # 4) 優先度(またはランダム等)で実行
        if "ポン" in actions:
            print("[AI] ポン選択")
            self.state.game.meld_manager.process_pon(1, self.state)
            return
        elif "チー" in actions:
            print("[AI] チー選択")
            chi_seq = self.state.game.meld_manager.meld_candidates["chi"][0]
            self.state.game.meld_manager.process_chi(1, chi_seq, self.state)
            return
        elif "カン" in actions:
            print("[AI] カン選択")
            kan_tile = self.state.game.meld_manager.meld_candidates["kan"][0]
            self.state.game.meld_manager.process_kan(1, kan_tile, self.state)
            return
        elif "ロン" in actions:
            print("[AI] ロン選択")
            # AIがロンする場合: process_ron(1, discard_tile, self.state)
            self.state.game.process_ron(1, discard_tile, self.state)
            return
        else:
            # 何もしない → プレイヤーのツモへ
            print("[AI] アクションなし → PLAYER_DRAW_PHASE")
            self.state.transition_to(PLAYER_DRAW_PHASE)

    def handle_event(self, event):
        """
        AIフェーズでは基本的に人間のクリックやキー操作は無視。
        必要に応じて追加
        """
        # まず共通処理を実行
        super().handle_event(event)
        pass
