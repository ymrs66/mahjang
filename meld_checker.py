# File: mahjang\meld_checker.py

from collections import Counter

class MeldChecker:
    """
    ポン/チー/カンなどの成立判定ロジックをまとめるクラス。
    ここでは "状態変更" は行わず、純粋に候補を計算して返すだけ。
    """

    @staticmethod
    def check_all_melds(tiles, pons, discard_tile):
        """
        ポン・チー・カンをまとめて判定し、それぞれの候補を返す。

        - tiles      : プレイヤーの手牌 (list of Tile)
        - pons       : プレイヤーのポン済みリスト (list of [Tile, Tile, Tile], ...)
        - discard_tile: 他家の捨て牌 (Tile) or None

        返り値: dict 形式
          {
            "pon_candidates": [...],
            "chi_candidates": [...],
            "kan_candidates": [...]
          }

        ※「暗槓」を含めたい場合は、下記にある can_kan(...) を discard_tile=None で別途呼び、
          その結果を合体するなどの処理を追加することも可能。
        """

        # 1) ポン候補
        pon_candidates = MeldChecker.can_pon(tiles, discard_tile)

        # 2) チー候補
        chi_candidates = MeldChecker.can_chi(tiles, discard_tile)

        # 3) カン候補
        kan_candidates = []
        #  (a) 明槓・加槓チェック
        tmp = MeldChecker.can_kan(tiles, pons, discard_tile)
        kan_candidates.extend(tmp)

        #  (b) 暗槓チェック
        #      discard_tile=None を指定して追加チェック
        #      すでに呼び出しているかどうかは好み次第
        tmp2 = MeldChecker.can_kan(tiles, pons, None)
        # 重複しないよう合体
        for kt in tmp2:
            if kt not in kan_candidates:
                kan_candidates.append(kt)

        return {
            "pon_candidates": pon_candidates,
            "chi_candidates": chi_candidates,
            "kan_candidates": kan_candidates,
        }

    # =================================================================
    # 以下、個別の判定メソッド(既存の can_pon, can_chi, can_kan, determine_kan_type)
    # =================================================================

    @staticmethod
    def can_pon(tiles, discard_tile):
        """
        ポン可能なら [[discard_tile, discard_tile, discard_tile]] のようなリストを返す。
        不可なら空リスト [] を返す。
        """
        if discard_tile is None:
            return []

        count = sum(1 for t in tiles if t.is_same_tile(discard_tile))
        if count >= 2:
            return [[discard_tile, discard_tile, discard_tile]]
        else:
            return []

    @staticmethod
    def can_chi(tiles, discard_tile):
        """
        チー可能な "順子候補" を複数返す (list of [Tile, Tile, Tile])。
        """
        if discard_tile is None:
            return []

        # スーツが数牌以外はチー不可
        suit = discard_tile.suit
        if suit not in ("m", "p", "s"):
            return []

        # discard_tile の数値変換
        try:
            discard_value = int(discard_tile.value)
        except ValueError:
            return []

        from collections import Counter
        same_suit_values = [int(t.value) for t in tiles if t.suit == suit]
        tile_counter = Counter(same_suit_values)

        chi_candidates = []
        chi_patterns = [ [-2, -1], [-1, 1], [1, 2] ]

        for offsets in chi_patterns:
            needed_values = [discard_value + off for off in offsets]
            if any(v < 1 or v > 9 for v in needed_values):
                continue

            # 全部そろっているか
            can_form = True
            for val in needed_values:
                if tile_counter[val] < 1:
                    can_form = False
                    break

            if can_form:
                used_temp = Counter()
                candidate_tiles = []
                for val in needed_values:
                    for t in tiles:
                        if t.suit == suit and int(t.value) == val:
                            if used_temp[val] < tile_counter[val]:
                                candidate_tiles.append(t)
                                used_temp[val] += 1
                                break
                new_sequence = candidate_tiles + [discard_tile]
                chi_candidates.append(new_sequence)

        return chi_candidates

    @staticmethod
    def can_kan(tiles, pons, discard_tile=None):
        """
        カンが可能かを判定し、候補となるTileオブジェクトのリストを返す。
          - 暗槓: discard_tile=None で 4枚そろっている
          - 明槓/加槓: discard_tile あり or すでにポンしている
        """
        from collections import Counter
        kan_candidates = []

        def count_in_hand(target_tile):
            return sum(1 for t in tiles if t.is_same_tile(target_tile))

        # （1）暗槓チェック
        if discard_tile is None:
            unique_tiles = []
            for t in tiles:
                if t not in unique_tiles:
                    unique_tiles.append(t)
            for ut in unique_tiles:
                if count_in_hand(ut) == 4:
                    kan_candidates.append(ut)
        else:
            # （2）明槓（discard_tile + 手札3枚）
            if count_in_hand(discard_tile) == 3:
                kan_candidates.append(discard_tile)

            # （3）加槓（既にポン済み + 手牌1枚）
            for ponset in pons:
                if len(ponset) == 3 and ponset[0].is_same_tile(discard_tile):
                    if count_in_hand(discard_tile) >= 1 and discard_tile not in kan_candidates:
                        kan_candidates.append(discard_tile)

        return kan_candidates

    @staticmethod
    def determine_kan_type(tiles, pons, discard_tile):
        """
        カンの種類 ('暗槓', '明槓', '加槓') を判別する。
        """
        if discard_tile is None:
            # 暗槓
            return "暗槓"

        # 明槓（捨て牌1枚 + 手牌3枚）
        count = sum(1 for t in tiles if t.is_same_tile(discard_tile))
        if count == 3:
            return "明槓"

        # 加槓（既にポン済み + 手牌1枚）
        for ponset in pons:
            if len(ponset) == 3 and ponset[0].is_same_tile(discard_tile):
                if sum(1 for t in tiles if t.is_same_tile(discard_tile)) == 1:
                    return "加槓"

        return None
