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
        # ここでwaiting_for_player_discard=Trueにするのは廃止
        # → 選択はもう select_tile_phase で行う

    def update(self, current_time):
        print("[PlayerDiscardPhase] update start")
        # (1) state.selected_tile が決まっているはず
        selected_tile = self.state.selected_tile
        if not selected_tile:
            print("[エラー] discard_phaseだが、selected_tileがNoneです！")
            # いったんスキップ or とりあえずAIへ？
            self.state.transition_to(AI_DRAW_PHASE)
            return

        # (2) 実際にゲーム上で捨てる
        self.game.discard_tile(selected_tile, 0)
        # 選択解除
        self.state.selected_tile = None
        # ツモ牌（drawn_tile）が使用された場合、クリアする
        self.state.drawn_tile = None

        # (3) AIへ移行
        self.state.ai_action_time = current_time + AI_ACTION_DELAY
        self.state.transition_to(AI_DRAW_PHASE)
    def handle_event(self, event):
        # まず共通処理を実行
        super().handle_event(event)
        pass

class AIDiscardPhase(BasePhase):
    def update(self, current_time):
        print("[AIDiscardPhase.update()] start")  # ここでフェーズの開始を明示
        if current_time < self.state.ai_action_time:
            print(f"  [AIDiscardPhase] AIの待機時間中: {current_time} < {self.state.ai_action_time}")
            return

        # AIがどの手牌を持っているか確認（調査用）
        print(f"  [AIDiscardPhase] AI手牌: {self.game.players[1].tiles}")

        discard_tile = self.game.players[1].discard_tile()
        print(f"  [AIDiscardPhase] discard_tile={discard_tile}")  # ← 追加

        # AIが捨て終わった後、プレイヤーの選択牌をクリア
        self.state.selected_tile = None

        if discard_tile is not None:
            print(f"  [AIDiscardPhase] AI chose tile to discard: {discard_tile}")
            self.game.discards[1].append(discard_tile)
            print(f"  [AIDiscardPhase] AIが牌を捨てました: {discard_tile}")
            print(f"  [AIDiscardPhase] discards[1]={self.game.discards[1]}")  # ← 追加: 現在のAI捨て牌リストを表示
            self.game.target_tile = discard_tile  # ← 明槓判定に利用
        else:
            print("  [エラー] AIが捨て牌を選択できませんでした！（discard_tile=None）")

        # ポン・チー・カン確認
        actions = self.game.get_available_actions(player_id=0, discard_tile=discard_tile)
        if actions:
            self.state.available_actions = actions
            print(f"  [AIDiscardPhase] プレイヤーが取り得るアクション: {actions}")
            self.state.transition_to(PLAYER_ACTION_SELECTION_PHASE)
            return

        self.state.ai_action_time = current_time + AI_ACTION_DELAY
        print("[AIDiscardPhase.update()] end → PLAYER_DRAW_PHASE")
        self.state.transition_to(PLAYER_DRAW_PHASE)
    def handle_event(self, event):
        # まず共通処理を実行
        super().handle_event(event)
        pass