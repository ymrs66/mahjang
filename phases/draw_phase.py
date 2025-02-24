# phases/draw_phase.py
from phases.base_phase import BasePhase
from core.constants import (
    GAME_END_PHASE,
    PLAYER_DRAW_PHASE,
    PLAYER_DISCARD_PHASE,
    PLAYER_ACTION_SELECTION_PHASE,  # ← 追加
    AI_DRAW_PHASE,
    AI_DISCARD_PHASE,
    AI_ACTION_DELAY
)

from meld_checker import is_win_hand  # ← 既にあるなら不要

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

        # --- ツモあがり判定を追加 ---
        # プレイヤーの手牌（14枚）を取得
        player_tiles = self.game.players[0].tiles  
        if is_win_hand(player_tiles):
            print("[ツモ判定] is_win_hand = True")
            print("[ツモ判定] プレイヤーが和了形です。ツモアクションを追加します。")

            # ★「スキップ」を含めず「ツモ」だけにする
            self.state.available_actions = ["ツモ"]

            # アクション選択フェーズへ
            self.state.transition_to(PLAYER_ACTION_SELECTION_PHASE)
            return
        else:
            print("[ツモ判定] is_win_hand = False -> 捨て牌フェーズへ")

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
        self.game.meld_manager.check_all_melds(1, None)  # discard_tile=None
        kan_candidates = self.game.meld_manager.meld_candidates["kan"]
        if kan_candidates:
            print(f"AIがカン可能: {kan_candidates}")
            self.game.process_kan(1, kan_candidates[0], self.state, "暗槓")
            self.state.ai_action_time = current_time + AI_ACTION_DELAY
            return

        # AIの14枚が和了形かチェック
        ai_tiles = self.game.players[1].tiles
        if is_win_hand(ai_tiles):
            print("[AI] ツモ和了可能！和了します。")
            # process_tsumo_ai() or 直接処理
            self.game.process_ai_tsumo(1, self.state)
            return

        # AIの捨てフェーズへ
        self.state.transition_to(AI_DISCARD_PHASE)
