# 手牌を管理するクラス
# hand.py
class Hand:
    def __init__(self):
        self.tiles = []  # 手牌のリスト

    def add_tile(self, tile):
        """牌を手牌に追加"""
        self.tiles.append(tile)

    def remove_tile(self, tile):
        """指定した牌を手牌から削除"""
        if tile in self.tiles:
            self.tiles.remove(tile)
        else:
            print(f"{tile} は手牌にありません")

    def sort_tiles(self):
        """手牌を並び替え"""
        self.tiles.sort(key=lambda t: (t.suit, t.value))

    def __repr__(self):
        return ", ".join(map(str, self.tiles))