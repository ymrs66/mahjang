##ai_player.py
from core.hand import Hand

class AIPlayer:
    def __init__(self, player_id):
        """
        AIプレイヤーの初期化
        :param player_id: プレイヤーID（通常は1以上）
        """
        self.id = player_id
        self.hand = Hand()  # 手牌を管理する Hand オブジェクト

    def add_tile(self, tile):
        """
        手牌に牌を追加
        """
        self.hand.add_tile(tile)  # Hand クラスの add_tile を利用

    def draw_tile(self, tile):
        """
        ツモ牌を手牌に追加し、並び替え
        :param tile: ツモった牌
        """
        self.add_tile(tile)
        self.hand.sort_tiles()  # 手牌を並べ替え

    def decide_discard(self):
        """
        捨てる牌を決定するロジック。
        現在は暫定的に最初の牌を捨てる。
        :return: 捨てる牌（Tile オブジェクト）または None
        """
        if not self.hand.tiles:
            return None
        # 暫定的に最初の牌を選択
        discard_tile = self.hand.tiles[0]
        print(f"AIが捨てる牌を決定: {discard_tile}")
        return discard_tile

    # AIPlayer の discard_tile メソッド
    def discard_tile(self):
        """
        AIが捨てる牌を選び、削除する。
        """
        discard_tile = self.decide_discard()  # 捨てる牌を選択
        if discard_tile:
            self.hand.remove_tile(discard_tile)  # 手牌から削除
            print(f"AIの捨て牌: {discard_tile}")  # デバッグ用
        return discard_tile