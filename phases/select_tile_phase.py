# file: mahjang/phases/select_tile_phase.py
from phases.base_phase import BasePhase
from core.constants import (
    PLAYER_SELECT_TILE_PHASE,
    PLAYER_DISCARD_PHASE,
    PLAYER_RIICHI_PHASE,
)
from meld_checker import is_14_tile_tenpai

class PlayerSelectTilePhase(BasePhase):
    """
    プレイヤーが手牌をクリックして捨て牌を選ぶ or リーチ宣言するためのフェーズ
    """

    def __init__(self, game, state):
        super().__init__(game, state)
        self.actions_shown = False

    def update(self, current_time):
        """
        毎フレーム呼ばれる。フェーズ開始直後にボタン表示などを行う。
        """
        if not self.actions_shown:
            self.build_available_actions()
            self.actions_shown = True

    def build_available_actions(self):
        """
        リーチ可能なら "リーチ" ボタン、通常は "捨てる" ボタンなどを state.available_actions に追加。
        """
        player = self.game.players[0]
        actions = []

        # 基本は「捨てる」ボタンは必須。
        actions.append("捨てる")

        # リーチ条件チェック
        #   門前かつ未リーチで、14枚テンパイしていれば "リーチ"
        if player.is_menzen and not player.is_reach and len(player.tiles) == 14:
            if is_14_tile_tenpai(player.tiles):
                print(actions)
                actions.append("リーチ")

        # スキップ系のボタンを入れる場合はここで追加
        # actions.append("スキップ") など

        self.state.available_actions = actions

    def handle_event(self, event):
        """
        このフェーズ中は「手牌クリック」と「ボタンクリック」を処理する。
        """
        import pygame
        # (1) 手牌クリック処理は従来と同様
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # 手牌をクリックして state.selected_tile を更新
            for i, tile in enumerate(self.game.players[0].tiles):
                # (TILE_WIDTH, TILE_MARGIN などは流用)
                # ここでクリック判定...
                pass

            # ボタン領域も判定
            for action, rect in self.state.action_buttons.items():
                if rect.collidepoint(pos):
                    if action == "捨てる":
                        self.discard_selected_tile()
                    elif action == "リーチ":
                        self.do_riichi()
                    # もしスキップがあれば skip() など

        # キー操作でスペース押下なら、捨てるのかスキップなのか決めるならここでもOK

    def discard_selected_tile(self):
        """
        選択された牌を確定し、PLAYER_DISCARD_PHASE へ遷移する
        """
        if self.state.selected_tile is not None:
            # 次のフェーズで捨てる動作を行う → discard_phaseへ
            self.state.transition_to(PLAYER_DISCARD_PHASE)
        else:
            print("[警告] 牌が選択されていません")


    def do_riichi(self):
        """
        リーチボタンが押されたときの処理:
          - 選択中の牌があればそれを切る
          - なければテンパイ牌を自動探索して切る
          - リーチフラグを立てて discard_phase へ
        """
        player = self.game.players[0]
        player.is_reach = True
        tile_to_discard = self.state.selected_tile

        # 選択牌がない場合は自動でテンパイ牌を探す
        if tile_to_discard is None:
            tile_to_discard = self.find_tenpai_tile()

        if tile_to_discard:
            # 本当にその牌を切ったらテンパイか確認したいなら:
            temp = player.tiles.copy()
            if tile_to_discard in temp:
                temp.remove(tile_to_discard)
                from meld_checker import is_tenpai
                if not is_tenpai(temp):
                    print("[エラー] 選択された牌(または自動探索した牌)を切ってもテンパイになりません!")
                    # キャンセルするか、別のUIを出すかはお好み
                    return
            else:
                print("[エラー] tile_to_discard が手牌にありません!")
                return

            # テンパイOKならリーチ成立 → PlayerDiscardPhaseで実際に捨てる
            print(f"[リーチ宣言] {tile_to_discard} を捨てます")
            self.state.selected_tile = tile_to_discard

            # フェーズ遷移: この後 discard_phase で自動的に捨てる
            self.state.transition_to(PLAYER_DISCARD_PHASE)
        else:
            print("[エラー] テンパイ牌が見つかりません。リーチ不能。")

    def find_tenpai_tile(self):
        """14枚のうち、切ったらテンパイになる牌を探索して返す。"""
        from meld_checker import is_tenpai
        player = self.game.players[0]
        for t in player.tiles:
            temp = player.tiles.copy()
            temp.remove(t)
            if is_tenpai(temp):
                return t
        return None