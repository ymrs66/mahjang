from tile import Tile
from hand import Hand
import random
from ai_player import AIPlayer

class Game:
    def __init__(self):
        self.wall = self.generate_wall()  # 山牌
        self.players = [Hand(), AIPlayer(1)]  # プレイヤー(0)とAI(1)
        self.discards = [[], []]  # プレイヤーの捨て牌[0]とAIの捨て牌[1]
        self.current_turn = 0  # 0: プレイヤー, 1: AI

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