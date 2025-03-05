# phases/riichi_phase.py

import pygame
from phases.base_phase import BasePhase
from core.constants import PLAYER_DISCARD_PHASE, PLAYER_RIICHI_PHASE, AI_ACTION_DELAY, AI_DRAW_PHASE
from meld_checker import is_tenpai  # 13枚の手牌がテンパイかどうか判定する関数

class PlayerRiichiPhase(BasePhase):
    """
    ツモ後にリーチができる場合、リーチするかどうかを選択するフェーズ。
    """
    def __init__(self, game, state):
        super().__init__(game, state)
        self.shown_buttons = False  # ボタンを描画したかどうかのフラグ

    def update(self, current_time):
        print("[PlayerRiichiPhase.update()] リーチorスキップ待ち")
        if not self.shown_buttons:
            # 「リーチ」ボタンを表示するため、available_actions に "リーチ" を設定
            self.state.available_actions = ["リーチ"]
            print("  [RiichiPhase] リーチボタンを表示します")
            self.shown_buttons = True

    def handle_event(self, event):
        # マウスクリックでボタン領域をチェック
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.state.action_buttons:
                for action, rect in self.state.action_buttons.items():
                    if rect.collidepoint(pos):
                        if action == "リーチ":
                            self.do_riichi()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            print("[RiichiPhase] スペースキーでスキップしました")
            self.skip_riichi()

    def do_riichi(self):
        """
        リーチの実行処理。候補牌が複数ある場合はその中から1枚自動で捨てる。
        """
        print("[RiichiPhase] リーチ宣言します")
        current_player = self.game.players[0]
        print("[RiichiPhase.do_riichi] ---------- リーチ判定開始 ----------")
        print("[RiichiPhase] 現在の手牌:", current_player.tiles)
        print("[RiichiPhase] 門前状態:", current_player.is_menzen, "リーチ済み:", current_player.is_reach)
        current_player.is_reach = True  # リーチフラグをONにする

        tile_to_discard = None

        # 既にユーザーが牌を選択している（=self.state.selected_tile != None）ならその牌を採用
        print(f"do_riichi,50,selected_tile: {self.state.selected_tile}")
        if self.state.selected_tile:
            tile_to_discard = self.state.selected_tile
            print(f"[リーチ] ユーザー選択牌: {tile_to_discard}")
        else:
            print("[リーチ] ユーザーが牌を選択していないため、自動探索に移行します。")

        if tile_to_discard:
            # いったんコピーして捨ててみる
            temp_hand = current_player.tiles.copy()
            temp_hand.remove(tile_to_discard)
            if is_tenpai(temp_hand):
                print("[リーチ] 選択された牌でリーチ可能です！")
            else:
                print("[リーチ] 選択された牌ではテンパイしません。リーチ不可！")
                # エラー表示・またはキャンセル処理など
                return

        # 選択がない場合は、手牌からリーチ候補（切ったときにテンパイになる牌）を自動で探す
        if not tile_to_discard:
            print(f"[RiichiPhase.do_riichi] 手動選択された牌={tile_to_discard}")
            print("[RiichiPhase] 選択牌がないので、リーチ候補を自動探索します")
            for tile in current_player.tiles:
                # 一時的に手牌からこの牌を除いた状態でテンパイかどうか判定
                temp_hand = current_player.tiles.copy()
                try:
                    temp_hand.remove(tile)
                except ValueError:
                    continue  # 万が一削除に失敗したら次へ
                if is_tenpai(temp_hand):
                    tile_to_discard = tile
                    break

        if tile_to_discard:
            print(f"[RiichiPhase] リーチ捨牌として自動選択された牌: {tile_to_discard}")
            self.game.discard_tile(tile_to_discard, 0)
            self.state.selected_tile = None
        else:
            # 万が一リーチ候補が見つからなければ、手牌の最後の牌を捨てる
            print("[RiichiPhase] リーチ候補が見つかりませんでした。手牌の最後の牌を捨てます")
            tile_to_discard = current_player.tiles[-1]
            self.game.discard_tile(tile_to_discard, 0)
            self.state.selected_tile = None

        # リーチ後は一定の待機時間を設けてからAIのツモフェーズへ移行
        self.state.ai_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY
        self.state.transition_to(AI_DRAW_PHASE)


    def skip_riichi(self):
        """
        リーチをスキップして、通常の捨牌フェーズへ進む処理
        """
        print("[RiichiPhase] リーチをスキップしてプレイヤー捨牌フェーズへ移行")
        self.state.transition_to(PLAYER_DISCARD_PHASE)
