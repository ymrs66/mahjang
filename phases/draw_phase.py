# File: mahjang\phases\draw_phase.py
from phases.base_phase import BasePhase
from core.constants import (
    GAME_END_PHASE,
    PLAYER_DRAW_PHASE,
    PLAYER_DISCARD_PHASE,
    PLAYER_ACTION_SELECTION_PHASE,
    PLAYER_RIICHI_PHASE,
    AI_DRAW_PHASE,
    AI_DISCARD_PHASE,
    AI_ACTION_DELAY
)

from meld_checker import is_win_hand, is_14_tile_tenpai

class PlayerDrawPhase(BasePhase):
    def update(self, current_time):
        # ▼ AIの待機時間に達していない場合は処理をスキップする
        if current_time < self.state.ai_action_time:
            return

        print(f"[デバッグ:PlayerDrawPhase] --- プレイヤーのツモフェーズ開始 ---")
        print(f"[デバッグ:PlayerDrawPhase] current_time={current_time}, ai_action_time={self.state.ai_action_time}")

        tile = self.game.draw_tile(0)
        if tile:
            print(f"[デバッグ:PlayerDrawPhase] プレイヤーがツモ: {tile}")
            self.game.players[0].add_tile(tile)
        else:
            print("[デバッグ:PlayerDrawPhase] 山が空です。ゲーム終了")
            self.state.transition_to(GAME_END_PHASE)
            return

        # プレイヤーの現在の手牌をログ出力（14枚になっているはず）
        player_tiles = self.game.players[0].tiles
        print(f"[デバッグ:PlayerDrawPhase] プレイヤーの手牌（14枚想定）: {player_tiles}")

        # --- ツモあがり判定 ---
        if is_win_hand(player_tiles):
            print("[ツモ判定] is_win_hand = True → 和了形！")
            print("[ツモ判定] 'ツモ'アクションを追加します")

            self.state.available_actions = ["ツモ"]
            self.state.transition_to(PLAYER_ACTION_SELECTION_PHASE)
            return
        else:
            print("[ツモ判定] is_win_hand = False → 捨て牌フェーズへ")

        # (2) リーチ判定（門前かつ未リーチでテンパイしているか）
        current_player = self.game.players[0]
        print(f"[デバッグ:PlayerDrawPhase] 門前状態={current_player.is_menzen}, リーチ済み={current_player.is_reach}")

        # phases/draw_phase.py の中
        if current_player.is_menzen and not current_player.is_reach:
            if is_14_tile_tenpai(player_tiles):
                print("[デバッグ:PlayerDrawPhase] テンパイ！ → 'リーチ'を選択できるフェーズへ移動します")
                self.state.transition_to(PLAYER_RIICHI_PHASE)
                return
            else:
                print("[デバッグ:PlayerDrawPhase] テンパイしていません → リーチ不可")

        # ここで現在のアクションリストを確認
        print(f"[デバッグ:PlayerDrawPhase] 現在の available_actions={self.state.available_actions}")

        # ツモ完了したらプレイヤーの捨て牌フェーズへ遷移
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
            self.game.process_ai_tsumo(1, self.state)
            return

        # AIの捨てフェーズへ
        self.state.transition_to(AI_DISCARD_PHASE)
