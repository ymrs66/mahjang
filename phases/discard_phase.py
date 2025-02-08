# phases/discard_phase.py
from phases.base_phase import BasePhase
from core.constants import (
    PLAYER_DRAW_PHASE,
    PLAYER_ACTION_SELECTION_PHASE,
    AI_DRAW_PHASE,
    AI_ACTION_DELAY
)

# phases/discard_phase.py

class PlayerDiscardPhase(BasePhase):
    def __init__(self, game, state):
        super().__init__(game, state)
        # フェーズが切り替わって「このクラスに入った」時点で waiting_for_player_discard を True にする
        # （初回呼び出しのタイミングでこれをやることを明示しておく）
        if not self.state.waiting_for_player_discard:
            print("[初回] プレイヤーの捨て牌待ちを開始します...")
            self.state.waiting_for_player_discard = True

    def update(self, current_time):
        print("[プレイヤー捨て牌フェーズ]")

        # もし waiting_for_player_discard が True なら、まだ入力中なので何もしない
        if self.state.waiting_for_player_discard:
            print("[待機] プレイヤーの捨て牌入力待ち...")
            return

        # ここに来るのは「捨てる操作が完了し、イベントハンドラで waiting_for_player_discard = False にされた後」のみ
        discard_tile = self.game.discards[0][-1] if self.game.discards[0] else None
        if discard_tile:
            actions = self.game.get_available_actions(0, discard_tile)
            if actions:
                self.state.available_actions = actions
                self.state.transition_to(PLAYER_ACTION_SELECTION_PHASE)
                return

        # アクションがなければAIへ
        self.state.ai_action_time = current_time + AI_ACTION_DELAY
        self.state.transition_to(AI_DRAW_PHASE)

class AIDiscardPhase(BasePhase):
    def update(self, current_time):
        if current_time < self.state.ai_action_time:
            return

        discard_tile = self.game.players[1].discard_tile()
        if discard_tile:
            self.game.discards[1].append(discard_tile)
            print(f"AIが牌を捨てました: {discard_tile}")

        # ポン・チー・カン確認
        actions = self.game.get_available_actions(player_id=0, discard_tile=discard_tile)
        if actions:
            self.state.available_actions = actions
            self.state.transition_to(PLAYER_ACTION_SELECTION_PHASE)
            return

        self.state.ai_action_time = current_time + AI_ACTION_DELAY
        self.state.transition_to(PLAYER_DRAW_PHASE)
