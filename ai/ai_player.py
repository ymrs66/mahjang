##ai_player.py
import random
from core.hand import Hand
from core.player import Player

class AIPlayer(Player):
    def __init__(self, player_id):
        super().__init__()  # Playerの __init__() で self.hand, self.pons 等が作られる
        self.id = player_id

    # AI専用のメソッドだけ追加する
    def decide_discard(self):
        """
        捨てる牌を決定するロジック。
        現在は暫定的に最初の牌を捨てる。
        :return: 捨てる牌（Tile オブジェクト）または None
        """
        if not self.hand.tiles:
            return None
        discard_tile = random.choice(self.hand.tiles)
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
            self.hand.sort_tiles() #並べ替え
            print(f"AIの捨て牌: {discard_tile}")  # デバッグ用
        return discard_tile