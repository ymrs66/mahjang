# tests/test_meld_check.py

import pytest
from core.game import Game
from core.tile import Tile

def test_pon_can_happen():
    """
    手牌に 1m,1m があるときに、捨て牌が 1m ならポン判定が通るかどうかのテスト。
    """
    # 1. ゲームオブジェクトを用意
    game = Game()

    # 2. プレイヤー0の手牌を強制的に 1m,1m にしてみる
    tile_1m_a = Tile('m', '1')
    tile_1m_b = Tile('m', '1')
    game.players[0].tiles.clear()
    game.players[0].tiles.extend([tile_1m_a, tile_1m_b])

    # 3. AIが捨てた牌を "1m" に仮定
    discard_tile = Tile('m', '1')

    # 4. check_pon を呼んで結果を確認
    pon_candidates = game.check_pon(player_id=0, discard_tile=discard_tile)

    # 5. pon_candidates が空でなければ「ポンできる」とみなす
    assert len(pon_candidates) > 0, "1m,1m + 捨て牌1m ならポン可能なはず"

def test_chi_can_happen():
    """
    手牌に 3m,4m を持ち、捨て牌が 2m の場合はチーできるか？
    """
    # 1. Gameインスタンス用意
    game = Game()

    # 2. プレイヤー0の手牌を強制セット
    tile_3m = Tile('m', '3')
    tile_4m = Tile('m', '4')
    game.players[0].tiles.clear()
    game.players[0].tiles.extend([tile_3m, tile_4m])

    # 3. discard_tile = 2m
    discard_tile = Tile('m', '2')

    # 4. check_chi でチー候補を取得
    chi_candidates = game.check_chi(player_id=0, discard_tile=discard_tile)

    # 5. チーが可能かどうか(リストがあるか)
    assert len(chi_candidates) > 0, "3m,4m + 捨て牌2m でチー可能"

def test_chi_cannot_happen_with_wrong_suit():
    """
    スーツが違う牌を捨てられてもチーはできないはず。
    例: 手牌=3m,4m, discard=2p => チー不可
    """
    game = Game()
    # 手牌: m3,m4
    game.players[0].tiles.clear()
    game.players[0].tiles.extend([Tile('m','3'), Tile('m','4')])
    # discard: p2
    discard_tile = Tile('p','2')

    # check_chi
    chi_candidates = game.check_chi(player_id=0, discard_tile=discard_tile)
    assert len(chi_candidates) == 0, "スーツが違えばチー不可"
