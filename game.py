from tile import Tile
from hand import Hand
import random
from ai_player import AIPlayer

class Game:
    def __init__(self):
        self.tile_cache = {}  # キャッシュ用辞書（修正案に基づく）
        self.wall = self.generate_wall()  # 山牌
        self.players = [Hand(), AIPlayer(1)]  # プレイヤー(0)とAI(1)
        self.discards = [[], []]  # プレイヤーの捨て牌[0]とAIの捨て牌[1]
        self.current_turn = 0  # 0: プレイヤー, 1: AI
        self.can_pon = False  # ポン可能フラグ
        self.target_tile = None  # ポン対象の牌

    def generate_wall(self):
        """麻雀の山を生成する"""
        suits = ['m', 'p', 's']
        honors = ['ton', 'nan', 'sha', 'pe', 'haku', 'hatsu', 'chun']
        wall = []

        for _ in range(4):  # 各牌を4回追加
            for suit in suits:
                for value in range(1, 10):
                    wall.append(Tile(suit, str(value), f"images/{value}{suit}.png"))
            for honor in honors:
                wall.append(Tile('z', honor, f"images/{honor}.png"))

        return wall

    def shuffle_wall(self):
        """山牌をシャッフル"""
        random.shuffle(self.wall)

    def draw_tile(self, player_id):
        """指定されたプレイヤーが山から1枚ツモる"""
        if self.wall:
            tile = self.wall.pop()
            return tile  # 配布や手牌追加は呼び出し元で行う
        else:
            print("山が空です！")
            return None

    def deal_initial_hand(self):
        """初期の手牌を配る"""
        for _ in range(13):
            # プレイヤーに配る
            tile = self.draw_tile(0)
            self.players[0].add_tile(tile)

            # AIに配る
            tile = self.draw_tile(1)
            self.players[1].add_tile(tile)

        print(f"初期配布完了: プレイヤー: {len(self.players[0].tiles)}枚, AI: {len(self.players[1].hand.tiles)}枚")

    def discard_tile(self, tile, player_id):
        """指定されたプレイヤーが牌を捨てる"""
        if player_id == 0:
            self.players[0].remove_tile(tile)  # プレイヤーの手牌から削除
            self.discards[0].append(tile)  # プレイヤーの捨て牌に追加
        else:
            self.players[1].discard_tile()  # AIが打牌
            self.discards[1].append(tile)  # AIの捨て牌に追加

    def check_pon(self, player_id, tile):
    
    #ポンが可能か判定する関数。
    #:param player_id: 判定するプレイヤーのID (通常は0: プレイヤー)
    #:param tile: 捨てられた牌
    #:return: ポン可能ならTrue、それ以外はFalse
    #"""
        if tile is None:  # tile が None の場合
            return False

        if player_id != 0:  # プレイヤー以外のポンは後で実装
            return False
        hand = self.players[player_id].tiles
        # 捨て牌と同じ牌が手牌に2枚以上あるかチェック
        count = sum(1 for t in hand if t.suit == tile.suit and t.value == tile.value)
        if count >= 2:
            self.can_pon = True
            self.target_tile = tile  # ポン対象の牌を設定
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
            print("ポン処理が無効です")
            return

        player_hand = self.players[player_id].tiles
        pon_tiles = [t for t in player_hand if t.suit == self.target_tile.suit and t.value == self.target_tile.value][:2]

        if len(pon_tiles) < 2:
            print("ポン対象の牌が手牌に不足しています")
            return

        # 手牌からポンの牌を削除
        for tile in pon_tiles:
            self.players[player_id].tiles = [
                t for t in self.players[player_id].tiles
                if not (t.suit == tile.suit and t.value == tile.value)
            ]

        # 捨て牌からポン対象牌を削除
        self.discards[1] = [
            t for t in self.discards[1]
            if not (t.suit == self.target_tile.suit and t.value == self.target_tile.value)
        ]

        # ポンした牌を記録 (右側に表示する用)
        self.players[player_id].pons.append(pon_tiles + [self.target_tile])

        print(f"ポン成功: {pon_tiles + [self.target_tile]}")
        self.can_pon = False  # ポン状態をリセット
        self.target_tile = None  # ターゲット牌をリセット