# phases/riichi_phase.py
import pygame
from phases.base_phase import BasePhase
from core.constants import (
    PLAYER_DISCARD_PHASE,
    PLAYER_RIICHI_PHASE,
    AI_ACTION_DELAY,
    AI_DRAW_PHASE
)

class PlayerRiichiPhase(BasePhase):
    """
    ツモ後にリーチができる場合、リーチするかどうかを選択するフェーズ。
    """
    def __init__(self, game, state):
        super().__init__(game, state)
        self.shown_buttons = False  # ボタンを描画したかどうかのフラグ

    def update(self, current_time):
        print("[PlayerRiichiPhase.update()] リーチorスキップ待ち")
        # ここでフェーズを勝手に変えない → ユーザーがクリックするまで待つ
        if not self.shown_buttons:
            # 「リーチ」と「スキップ」を選択肢に追加
            self.state.available_actions = ["リーチ"]
            print("  [RiichiPhase] ボタン表示準備")
            self.shown_buttons = True

    def handle_event(self, event):
        # ここでマウスクリックを拾う
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.state.action_buttons:
                for action, rect in self.state.action_buttons.items():
                    if rect.collidepoint(pos):
                        if action == "リーチ":
                            self.do_riichi()
                            
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # スキップ扱いにする例
            print("[RiichiPhase] スペースキーでスキップしました")
            self.skip_riichi()

    def do_riichi(self):
        """
        リーチの実行処理。
        """
        print("[RiichiPhase] リーチ宣言します")
        current_player = self.game.players[0]
        current_player.is_reach = True  # リーチフラグON

        # 例: リーチ棒を場に出す処理などあればここで行う
        # ...

        # リーチ時の捨て牌を強制する（選択されている牌を使う or 自動）
        tile_to_discard = self.state.selected_tile
        if tile_to_discard:
            self.game.discard_tile(tile_to_discard, 0)
            self.state.selected_tile = None
        else:
            print("[RiichiPhase] リーチ捨て牌が選択されていません。暫定で手牌の最後を捨てるなど...")

        # リーチ後は AIのターンへ（または鳴きチェックへ）進行
        # 次フェーズへ
        self.state.ai_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY
        self.state.transition_to(AI_DRAW_PHASE)

    def skip_riichi(self):
        """
        リーチをスキップして、通常の捨て牌フェーズへ行く
        """
        print("[RiichiPhase] リーチをスキップ -> プレイヤー捨て牌フェーズへ")
        self.state.transition_to(PLAYER_DISCARD_PHASE)
