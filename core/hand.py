## 手牌を管理するクラス
# hand.py
class Hand:
    def __init__(self):
        self.tiles = []  # 手牌のリスト
        self.pons = []   # ポンした牌のリスト
        self.chis = []   # チーした牌のリスト
        self.kans = []  # カンされた牌を記録するリスト

    def add_tile(self, tile):
        """牌を手牌に追加"""
        self.tiles.append(tile)

    def remove_tile(self, tile):
    #指定した牌を手牌から1枚だけ削除（同一個体優先→値同値フォールバック）"""
    # 1) identity（同一オブジェクト）で狙い撃ち
        for i, t in enumerate(self.tiles):
            if t is tile:
                del self.tiles[i]
                return True
    # 2) 見つからなければ値同値で1枚だけ除去
        for i, t in enumerate(self.tiles):
            if getattr(t, "is_same_tile", lambda _o: False)(tile):
                del self.tiles[i]
                return True
        print(f"[Hand.remove_tile] 指定牌が見つかりません: {tile} / 手牌={self.tiles}")
        return False

    def add_chi(self, sequence, discard_tile):
        """
        チーした順子を追加
        順子内の牌は手牌から削除されるが、捨て牌は手牌に存在しないため除外
        """
        print(f"チー処理開始: sequence={sequence}, discard_tile={discard_tile}")
        if all(any(t.is_same_tile(tile) for t in self.tiles) for tile in sequence if not tile.is_same_tile(discard_tile)):
            self.chis.append(sequence)  # 順子をチーリストに追加
            # 値同値で2枚だけ除去
            for tile in sequence:
                if not tile.is_same_tile(discard_tile):
                    for i, t in enumerate(self.tiles):
                        if t.is_same_tile(tile):
                            del self.tiles[i]
                            break
            print(f"チーを実行しました: {sequence}")
            print(f"現在の手牌: {self.tiles}")
            print(f"現在のチーリスト: {self.chis}")
        else:
            raise ValueError("順子の一部が手牌に存在しません")

    def sort_tiles(self):
        """手牌を並び替え"""
        self.tiles.sort(key=lambda t: (t.suit, t.value))

    def __repr__(self):
        return f"Tiles: {', '.join(map(str, self.tiles))} | Pons: {self.pons} | Chis: {self.chis}"