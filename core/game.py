# File: mahjang\core\game.py

import random
from core.tile import Tile
from core.hand import Hand
from ai.ai_player import AIPlayer
from core.player import Player
from core.constants import *
# meld_checker.py をインポート
from meld_checker import MeldChecker

class Game:
    def __init__(self):
        self.tile_cache = {}
        self.wall = self.generate_wall()
        self.players = [Player(), AIPlayer(1)]
        self.discards = [[], []]

        # フラグや候補 (ポン／チー／カン) はここで保持
        self.can_pon = False
        self.can_chi = False
        self.can_kan = False
        self.target_tile = None
        self.pon_candidates = []
        self.chi_candidates = []
        self.kan_candidates = []

    def generate_wall(self):
        wall = []
        for _ in range(4):
            for suit in SUITS:
                for value in range(1, 10):
                    wall.append(Tile(suit, str(value), TILE_IMAGE_PATH.format(value=value, suit=suit)))
            for honor in HONORS:
                wall.append(Tile('z', honor, TILE_IMAGE_PATH.format(value=honor, suit='')))
        return wall

    def shuffle_wall(self):
        random.shuffle(self.wall)

    def draw_tile(self, player_id):
        if self.wall:
            return self.wall.pop()
        else:
            return None

    def deal_initial_hand(self):
        for _ in range(13):
            self.players[0].add_tile(self.draw_tile(0))
            self.players[1].add_tile(self.draw_tile(1))
        print(f"初期配布完了: プレイヤー: {len(self.players[0].tiles)}枚, "
              f"AI: {len(self.players[1].tiles)}枚")

    def is_game_over(self):
        return len(self.wall) == 0

    # ============================================
    #  追加: まとめて(ポン/チー/カン)判定し、フラグを更新するメソッド
    # ============================================
    def check_all_melds_in_game(self, player_id, discard_tile):
        """
        MeldChecker.check_all_melds(...) を呼び出し、
        その結果を self.can_pon, self.pon_candidates,
                    self.can_chi, self.chi_candidates,
                    self.can_kan, self.kan_candidates
        に反映する。
        """
        tiles = self.players[player_id].tiles
        pons  = self.players[player_id].pons

        result = MeldChecker.check_all_melds(tiles, pons, discard_tile)

        # ポン情報を更新
        self.pon_candidates = result["pon_candidates"]
        self.can_pon = (len(self.pon_candidates) > 0)

        # チー情報を更新
        self.chi_candidates = result["chi_candidates"]
        self.can_chi = (len(self.chi_candidates) > 0)

        # カン情報を更新
        self.kan_candidates = result["kan_candidates"]
        self.can_kan = (len(self.kan_candidates) > 0)

        # target_tile は discard_tile を共有
        # もし暗槓のために discard_tile=None を呼んでいたらどうする？ → お好みでロジックを決める
        # ここでは「捨て牌があればそれをtarget_tileとする」方針
        if discard_tile is not None:
            self.target_tile = discard_tile
        else:
            # 暗槓だけのケースなら self.target_tile をどうするかは任意
            pass

        return result

    # ============================================
    # get_available_actions 内で "まとめて" 判定を呼ぶ
    # ============================================
    def get_available_actions(self, player_id, discard_tile):
        """
        ポン/チー/カン判定をまとめて呼び出し、
        実行可能なアクション名をリストで返す。
        """

        # 1) まとめてチェック
        self.check_all_melds_in_game(player_id, discard_tile)

        # 2) フラグに応じてアクション名を追加
        actions = []
        if self.can_pon:
            actions.append("ポン")
        if self.can_chi:
            actions.append("チー")
        if self.can_kan:
            actions.append("カン")
        return actions

    def determine_kan_type(self, player_id, tile):
        """
        MeldChecker.determine_kan_type(...) を呼び出す。
        """
        discard_tile = self.target_tile
        return MeldChecker.determine_kan_type(
            self.players[player_id].tiles,
            self.players[player_id].pons,
            discard_tile
        )

    def discard_tile(self, tile, player_id):
        if player_id == 0:
            print(f"手牌から捨てます: {tile}")
            self.players[0].discard_tile(tile)
            self.discards[0].append(tile)

            # リセット
            self.can_pon = False
            self.can_chi = False
            self.can_kan = False
            self.target_tile = None
        else:
            discarded_tile = self.players[1].discard_tile()
            if discarded_tile:
                self.discards[1].append(discarded_tile)
                print(f"AIが捨てた牌: {discarded_tile}")
            else:
                print("エラー: AIが捨て牌を選択できませんでした！")

    def process_pon(self, player_id, state):
        print("[デバッグ] process_pon に入りました")
        print(f"[デバッグ] can_pon={self.can_pon}, target_tile={self.target_tile}")
        if not self.can_pon or self.target_tile is None:
            return
        player_hand = self.players[player_id].tiles
        pon_tiles = [t for t in player_hand if t.is_same_tile(self.target_tile)][:2]
        print(f"[デバッグ] pon候補の枚数={len(pon_tiles)}, pon_tiles={pon_tiles}")
        if len(pon_tiles) < 2:
            print("ポン対象の牌が手牌に不足しています")
            return

        # 手牌から2枚除去
        for tile in pon_tiles:
            self.players[player_id].remove_tile(tile)
        # 相手の捨て牌から1枚除去
        self.discards[1] = [t for t in self.discards[1] if not t.is_same_tile(self.target_tile)]

        # ポンセットに加える
        self.players[player_id].pons.append(pon_tiles + [self.target_tile])

        print(f"ポン成功: {pon_tiles + [self.target_tile]}")
        self.can_pon = False
        self.target_tile = None

        state.waiting_for_player_discard = False
        state.transition_to(PLAYER_DISCARD_PHASE)

    def process_chi(self, player_id, chosen_sequence, state):
        if self.target_tile is None:
            print("エラー: target_tile が None です。")
            return
        player_hand = self.players[player_id].tiles
        seq_without_discard = [tile for tile in chosen_sequence if not tile.is_same_tile(self.target_tile)]
        if not all(t in player_hand for t in seq_without_discard):
            print("エラー: 手牌に不足があります")
            return

        # 手牌から2枚除去
        for tile in seq_without_discard:
            self.players[player_id].remove_tile(tile)
        # 捨て牌から1枚除去
        self.discards[1] = [t for t in self.discards[1] if not t.is_same_tile(self.target_tile)]

        # チーセットに加える
        self.players[player_id].chis.append(chosen_sequence)

        print(f"チー成功: {chosen_sequence}")
        self.can_chi = False
        self.target_tile = None

        state.waiting_for_player_discard = False
        state.transition_to(PLAYER_DISCARD_PHASE)

    def process_kan(self, player_id, tile, state, kan_type):
        """
        カンの処理 (暗槓, 明槓, 加槓)。
        """
        if kan_type == '暗槓':
            # ...
            pass
        elif kan_type == '明槓':
            # ...
            pass
        elif kan_type == '加槓':
            # ...
            pass

        # 嶺上牌ツモ など ...
