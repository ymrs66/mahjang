# phases/riichi_phase.py
import pygame
from phases.base_phase import BasePhase
from core.constants import (
    PLAYER_RIICHI_PHASE,
    PLAYER_DISCARD_PHASE,
    AI_DRAW_PHASE,
    AI_ACTION_DELAY
)
from meld_checker import is_tenpai

class PlayerRiichiPhase(BasePhase):
    """
    リーチ専用フェーズ:
      - 14枚 + 門前＋未リーチ + テンパイ のときに遷移
      - ボタンで「リーチ」 or 「スキップ」などを選ぶ
    """

    def __init__(self, game, state):
        super().__init__(game, state)
        # ボタンを表示したかどうか
        self.shown_buttons = False

    def update(self, current_time):
        # 1) 初回にリーチ用のボタンを作成（"リーチ","スキップ"）
        if not self.shown_buttons:
            self.state.available_actions = ["リーチ", "スキップ"]
            print("[RiichiPhase] リーチボタンを表示します")
            self.shown_buttons = True

        # 2) ここで「ユーザーがボタンクリックするのを待つ」 -> イベントハンドラ内で処理
        #    クリックされるまでフェーズは継続。
        #    何もしないで return するとフェーズが止まって待機するイメージ

    def handle_event(self, event):
        """リーチフェーズ内でのマウスクリック or キー押下を処理"""
        import pygame
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # 各ボタンのRectが state.action_buttons にあるとして、
            # どのボタンがクリックされたかチェック
            for action, rect in self.state.action_buttons.items():
                if rect.collidepoint(pos):
                    if action == "リーチ":
                        self.do_riichi()
                    elif action == "スキップ":
                        self.skip_riichi()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # スキップ扱い
                self.skip_riichi()

    def do_riichi(self):
        """実際のリーチ実行処理"""
        player = self.game.players[0]
        print("[RiichiPhase] リーチ宣言します")
        # 1) フラグをON
        player.is_reach = True

        # 2) リーチ捨牌を決める
        tile_to_discard = self.state.selected_tile
        if tile_to_discard is None:
            # 自動探索（テンパイになる牌を探す）
            tile_to_discard = self.find_tenpai_tile()

        if tile_to_discard:
            # 一時的に手牌から除いてテンパイ判定
            temp = player.tiles.copy()
            if tile_to_discard in temp:
                temp.remove(tile_to_discard)
                if is_tenpai(temp):
                    print(f"[RiichiPhase] リーチ可能！捨て牌: {tile_to_discard}")
                    self.game.discard_tile(tile_to_discard, 0)
                    self.state.transition_to(PLAYER_DISCARD_PHASE)
                else:
                    print("[エラー] 選択牌を切ってもテンパイになりません。リーチ無効！")
                    # ここではエラー扱い
                    # 通常は「再選択させる」等が必要
            else:
                print("[エラー] selected_tile が手牌にありません")
        else:
            print("[RiichiPhase] リーチ候補が見つかりませんでした。スキップします。")

        # 3) フェーズ移行
    def find_tenpai_tile(self):
        """
        切ったときテンパイになる牌を探して返す
        """
        from meld_checker import is_tenpai
        player = self.game.players[0]
        for tile in player.tiles:
            temp = player.tiles.copy()
            temp.remove(tile)
            if is_tenpai(temp):
                return tile
        return None
    def skip_riichi(self):
        """リーチしない場合の処理"""
        print("[RiichiPhase] リーチをスキップします")
        # 通常の捨牌フェーズに戻す
        self.state.transition_to(PLAYER_DISCARD_PHASE)  # PLAYER_DISCARD_PHASE=0

    def find_tenpai_tile(self):
        """
        14枚の中で、切ったときにテンパイになる牌を探して返す
        """
        player = self.game.players[0]
        from meld_checker import is_tenpai
        for tile in player.tiles:
            temp_hand = player.tiles.copy()
            temp_hand.remove(tile)
            if is_tenpai(temp_hand):
                return tile
        return None
