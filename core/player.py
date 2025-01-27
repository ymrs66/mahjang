# player.py
from core.hand import Hand

class Player:
    def __init__(self):
        self.hand = Hand()
        self.pons = []
        self.chis = []
        self.kans = []

    @property
    def tiles(self):
        return self.hand.tiles

    def draw_tile(self, tile):
        self.hand.add_tile(tile)
        self.hand.sort_tiles()

    def remove_tile(self, tile):
        """手牌から指定牌を除去して並べ替える"""
        self.hand.remove_tile(tile)
        self.hand.sort_tiles()

    def discard_tile(self, tile):
        """プレイヤーが1枚捨てる(人間用)"""
        # 通常は remove_tile と同じ動作
        # 追加で "捨てる" 表示 or ログ出力をしてもいい
        self.remove_tile(tile) # 手牌から取り除く処理
        print("捨てる処理...")  # 例えば捨てるアニメやログなど追加処理を出す

    def add_tile(self, tile):
        """プレイヤーが牌を引く (Handのadd_tileを呼ぶ)"""
        self.hand.add_tile(tile)
