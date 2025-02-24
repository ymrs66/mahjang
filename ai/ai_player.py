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
        if not self.hand.tiles:
            print("  [AIPlayer.decide_discard] 手牌が空です。Noneを返します。")
            return None
        discard_tile = random.choice(self.hand.tiles)
        print(f"  [AIPlayer.decide_discard] ランダムに選んだ捨て牌: {discard_tile}")
        return discard_tile

    def discard_tile(self):
        print("  [AIPlayer.discard_tile()] start")
        discard_tile = self.decide_discard()  # 捨てる牌を選択
        print(f"  [AIPlayer.discard_tile] decide_discard() => {discard_tile}")

        if discard_tile:
            print(f"  [AIPlayer] discard_tile={discard_tile}, 手牌から除去します...")
            self.hand.remove_tile(discard_tile)
            self.hand.sort_tiles()
            print(f"  [AIPlayer] remove後の手牌: {self.hand.tiles}")
            print(f"AIの捨て牌: {discard_tile}")
        else:
            print("  [AIPlayer] discard_tile=None 何も捨てません。")
        print("  [AIPlayer.discard_tile()] end")
        return discard_tile
