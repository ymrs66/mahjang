from hand import Hand

class AIPlayer:
    def __init__(self, player_id):
        self.id = player_id
        self.hand = Hand()  # 手牌を管理する Hand オブジェクト

    def add_tile(self, tile):
        """手牌に牌を追加"""
        self.hand.add_tile(tile)  # Hand クラスの add_tile を利用

    def draw_tile(self, tile):
        """ツモ牌を手牌に追加"""
        self.add_tile(tile)  # add_tile を利用して手牌に追加
        self.hand.sort_tiles()  # 手牌を並べ替え

    def decide_discard(self):
        """
        捨てる牌を決定。
        - 現在は暫定的に最初の牌を捨てる。
        - 将来的に捨てる牌の選択ロジックを最適化可能。
        """
        if not self.hand.tiles:
            return None
        return self.hand.tiles[0]  # 暫定的に最初の牌を選択

    def discard_tile(self):
        """AIが捨てる牌を選び、削除する"""
        discard_tile = self.decide_discard()  # 捨てる牌を決定
        if discard_tile:
            self.hand.remove_tile(discard_tile)  # 手牌から削除
        return discard_tile
