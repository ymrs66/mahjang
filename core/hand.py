## 手牌を管理するクラス
# hand.py
class Hand:
    def __init__(self):
        self.tiles = []  # 手牌のリスト
        self.pons = []   # ポンした牌のリスト
        self.chis = []   # チーした牌のリスト

    def add_tile(self, tile):
        """牌を手牌に追加"""
        self.tiles.append(tile)

    def remove_tile(self, tile):
        """指定した牌を手牌から削除"""
        if tile in self.tiles:
            self.tiles.remove(tile)
        else:
            print(f"{tile} は手牌にありません")

    def add_chi(self, sequence):
        """
        チーした順子を追加
        順子内の牌は手牌から削除される
        """
        if all(tile in self.tiles for tile in sequence[:-1]):  # 最後の牌は捨て牌
            self.chis.append(sequence)  # 順子をチーリストに追加
            for tile in sequence[:-1]:  # 捨て牌以外を削除
                self.tiles.remove(tile)
        else:
            raise ValueError("順子の一部が手牌に存在しません")

    def sort_tiles(self):
        """手牌を並び替え"""
        self.tiles.sort(key=lambda t: (t.suit, t.value))

    def __repr__(self):
        return f"Tiles: {', '.join(map(str, self.tiles))} | Pons: {self.pons} | Chis: {self.chis}"