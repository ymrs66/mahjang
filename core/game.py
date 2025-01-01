##game.py
import random
from core.tile import Tile
from core.hand import Hand
from ai.ai_player import AIPlayer
from core.constants import SUITS, HONORS, TILE_IMAGE_PATH

class Game:
    def __init__(self):
        self.tile_cache = {}  # キャッシュ用辞書（未使用であれば削除検討）
        self.wall = self.generate_wall()  # 山牌
        self.players = [Hand(), AIPlayer(1)]  # プレイヤー(0)とAI(1)
        self.discards = [[], []]  # プレイヤーの捨て牌[0]とAIの捨て牌[1]
        self.current_turn = 0  # 0: プレイヤー, 1: AI
        self.can_pon = False  # ポン可能フラグ
        self.can_chi = False  # チー可能フラグ
        self.target_tile = None  # ポン/チー対象の牌
        self.chi_candidates = []  # チー候補のリストを初期化

    def is_game_over(self):
        """
        ゲーム終了条件を判定する。
        山牌がなくなった場合にTrueを返す。
        """
        return len(self.wall) == 0

    def generate_wall(self):
        """麻雀の山を生成する"""
        wall = []
        for _ in range(4):  # 各牌を4回追加
            for suit in SUITS:
                for value in range(1, 10):
                    wall.append(Tile(suit, str(value), TILE_IMAGE_PATH.format(value=value, suit=suit)))
            for honor in HONORS:
                # 字牌の画像パスには 'z' を除く
                wall.append(Tile('z', honor, TILE_IMAGE_PATH.format(value=honor, suit='')))
        return wall


    def shuffle_wall(self):
        """山牌をシャッフル"""
        random.shuffle(self.wall)

    def draw_tile(self, player_id):
        """指定されたプレイヤーが山から1枚ツモる"""
        if self.wall:
            return self.wall.pop()
        else:
            print("山が空です！")
            return None

    def deal_initial_hand(self):
        """初期の手牌を配る"""
        for _ in range(13):
            self.players[0].add_tile(self.draw_tile(0))  # プレイヤー
            self.players[1].add_tile(self.draw_tile(1))  # AI
        print(f"初期配布完了: プレイヤー: {len(self.players[0].tiles)}枚, AI: {len(self.players[1].hand.tiles)}枚")

    def discard_tile(self, tile, player_id):
        print(f"discard_tile 呼び出し: tile={tile}, player_id={player_id}")
        if player_id == 0:
            if tile in self.players[0].tiles:
                print(f"手牌から削除: {tile}")
                self.players[0].remove_tile(tile)
                self.discards[0].append(tile)
            else:
                print(f"エラー: {tile} は手牌に存在しません！")
        else:
            discarded_tile = self.players[1].discard_tile()
            self.discards[1].append(discarded_tile)
            print(f"AIが捨てた牌: {discarded_tile}")

    def check_pon(self, player_id, tile):
        """
        ポンが可能か判定する。
        """
        if tile is None or player_id != 0:  # 現在はプレイヤーのみ実装
            return False
        hand = self.players[player_id].tiles
        count = sum(1 for t in hand if t.suit == tile.suit and t.value == tile.value)
        if count >= 2:
            self.can_pon = True
            self.target_tile = tile
            return True
        else:
            self.can_pon = False
            self.target_tile = None
            return False

    def process_pon(self, player_id):
        """
        ポン処理を実行する。
        """
        if not self.can_pon or self.target_tile is None:
            return

        # 手牌から2枚、捨て牌から1枚を取得
        player_hand = self.players[player_id].tiles
        pon_tiles = [t for t in player_hand if t.suit == self.target_tile.suit and t.value == self.target_tile.value][:2]
        if len(pon_tiles) < 2:
            print("ポン対象の牌が手牌に不足しています")
            return

        # 手牌と捨て牌を更新
        for tile in pon_tiles:
            self.players[player_id].tiles.remove(tile)
        if self.target_tile in self.discards[1]:
            self.discards[1].remove(self.target_tile)
        self.players[player_id].pons.append(pon_tiles + [self.target_tile])

        print(f"ポン成功: {pon_tiles + [self.target_tile]}")
        self.can_pon = False
        self.target_tile = None
        self.current_turn = player_id  # ポンしたプレイヤーのターンに戻る

    def check_chi(self, player_id, discard_tile):
        """
        チー可能な牌の組み合わせをチェック
        """
        player_hand = self.players[player_id].tiles
        discard_suit = discard_tile.suit

        print(f"チー判定開始: プレイヤー{player_id}, 捨て牌: {discard_tile}")
    
        # 捨て牌が数牌でない場合はチー不可
        if discard_suit not in ["m", "p", "s"]:
            print("チー不可: 捨て牌が数牌ではありません")
            return []

        try:
            discard_value = int(discard_tile.value)  # 数牌の場合、値を整数型に変換
        except ValueError:
            print("チー不可: 捨て牌の値が整数に変換できません")
            return []

        chi_candidates = []

        # チー候補を探す
        for offset in [-2, -1, 1]:  # -2/-1, -1/+1, +1/+2 の組み合わせを確認
            needed_values = [
                discard_value + offset,
                discard_value + (2 * offset)
            ]
            print(f"必要な値: {needed_values} (オフセット: {offset})")

            # 必要な牌が手牌にあるか確認
            candidate = [
                tile for tile in player_hand
                if tile.suit == discard_suit and int(tile.value) in needed_values
            ]

            # 候補が2枚揃った場合
            if len(candidate) == 2:
                candidate.append(discard_tile)  # 捨て牌を含める
                chi_candidates.append(candidate)
                print(f"チー候補に追加: {candidate}")

        if chi_candidates:
            self.target_tile = discard_tile  # ターゲット牌を設定

        print(f"最終的なチー候補: {chi_candidates}")
        return chi_candidates

    def process_chi(self, player_id, chosen_sequence):
        """
        チー処理を実行する。
        """
        if self.target_tile is None:
            print("エラー: target_tile が None です。")
            return

        print(f"チー処理開始: プレイヤー{player_id}, 選択された順子: {chosen_sequence}")
        player_hand = self.players[player_id].tiles  # プレイヤーの手牌を取得

        # 捨て牌を除外した順子部分を取得
        sequence_without_discard = [tile for tile in chosen_sequence if not (
            tile.suit == self.target_tile.suit and tile.value == self.target_tile.value
        )]

        # 手牌に必要な牌が揃っているか確認
        if not all(tile in player_hand for tile in sequence_without_discard):
            print(f"エラー: {sequence_without_discard} の一部が手牌に存在しません")
            return

        # チー牌を手牌から削除
        for tile in sequence_without_discard:
            self.players[player_id].remove_tile(tile)

        # 捨て牌を捨て牌リストから削除
        if self.target_tile in self.discards[1]:  # AIが捨てた牌から削除
            self.discards[1].remove(self.target_tile)

        # チーした牌を記録
        self.players[player_id].chis.append(chosen_sequence)  # 順子をチーリストに追加

        print(f"チー成功: {chosen_sequence}")
        self.can_chi = False  # チー状態をリセット
        self.target_tile = None  # ターゲット牌をリセット