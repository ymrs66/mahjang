# phases/draw_phase.py
from phases.base_phase import BasePhase
from core.constants import (
    GAME_END_PHASE,
    PLAYER_DRAW_PHASE,
    PLAYER_DISCARD_PHASE,
    AI_DRAW_PHASE,
    AI_DISCARD_PHASE,
    AI_ACTION_DELAY
)

class PlayerDrawPhase(BasePhase):
    def update(self, current_time):
        if current_time < self.state.ai_action_time:
            return

        tile = self.game.draw_tile(0)
        if tile:
            print(f"プレイヤーがツモ: {tile}")
            self.game.players[0].add_tile(tile)
        else:
            print("山が空です。ゲーム終了")
            self.state.transition_to(GAME_END_PHASE)
            return

        # ツモ後のカン判定など必要ならこちらで
        # e.g. kan_candidates = self.game.check_kan(0)
        # ...

        # ツモ完了したらプレイヤーの捨て牌フェーズへ
        self.state.transition_to(PLAYER_DISCARD_PHASE)


class AIDrawPhase(BasePhase):
    def update(self, current_time):
        if current_time < self.state.ai_action_time:
            return

        print("[AIツモフェーズ] AIがツモを行います")
        tile = self.game.draw_tile(1)
        if tile:
            self.game.players[1].draw_tile(tile)
            print(f"AIがツモ: {tile}")
        else:
            print("山が空です。ゲーム終了")
            self.state.transition_to(GAME_END_PHASE)
            return

        # カン判定など
        self.game.check_all_melds_in_game(player_id=1, discard_tile=None)  # or discard_tile
        kan_candidates = self.game.meld_candidates["kan"]  # これでカン候補が取れる
        if kan_candidates:
            print(f"AIがカン可能: {kan_candidates}")
            self.game.process_kan(1, kan_candidates[0], self.state, "暗槓")
            self.state.ai_action_time = current_time + AI_ACTION_DELAY
            return

        # AIの捨てフェーズへ
        self.state.transition_to(AI_DISCARD_PHASE)
