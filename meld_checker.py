# File: mahjang\meld_checker.py

from collections import Counter

def is_win_hand(tiles_14):
    # 1) 同じ形式にソート or suit, value に分解したリストを作る
    sorted_list = convert_tiles_to_sorted(tiles_14)
    
    # 2) 雀頭候補を列挙
    for i in range(len(sorted_list) - 1):
        if sorted_list[i] == sorted_list[i+1]:
            # 雀頭候補が見つかった
            head_tile = sorted_list[i]

            # 雀頭2枚を抜いた残りをメンツ分解
            new_list = remove_two_tiles(sorted_list, i, i+1)  # i番目とi+1番目を除去
            if check_4_melds(new_list):
                return True
    return False

def check_4_melds(tiles_12):
    # ベースケース
    if len(tiles_12) == 0:
        return True
    
    # 先頭牌を取り出す (タプル: (suit_id, val))
    first = tiles_12[0]
    
    # (1) 刻子チェック
    if tiles_12.count(first) >= 3:
        # 先頭と同じ牌3枚を除去
        new_list = remove_three_tiles(tiles_12, first, first, first)
        if new_list is not None and check_4_melds(new_list):
            return True
    
    # (2) 順子チェック
    suit_id, val = first
    # 先頭が字牌(suit_id==3)だったら順子は作れない
    if suit_id < 3:
        # is_sequence_possible(tiles_12) も suit_id/val をチェックしているならOK
        if is_sequence_possible(tiles_12):
            new_list = remove_sequence(tiles_12,
                                       (suit_id, val),
                                       (suit_id, val + 1),
                                       (suit_id, val + 2))
            if new_list is not None and check_4_melds(new_list):
                return True
    
    # 失敗
    return False

def convert_tiles_to_sorted(tiles_14):
    """
    14枚の Tile オブジェクトのリストを受け取り、
    (suit, value) のタプルなどに変換してソートしたリストを返す例。
    'm'/'p'/'s'なら数値、'z'なら別途優先度を割り当てるなどの仕組み。
    """
    # suitを整数にマッピングする例: m->0, p->1, s->2, z->3
    suit_priority = {'m': 0, 'p': 1, 's': 2, 'z': 3}

    converted = []

    for tile in tiles_14:
        s = tile.suit
        # 字牌(z)なら tile.value は 'ton','nan'... or 'haku','chun' など
        # 数牌(m,p,s)なら '1'〜'9'
        # ここではスーツごとの優先度を suit_priority[s] とし、
        # 値は数牌なら int(tile.value)、字牌なら任意の並び順にマッピング
        if s in ('m', 'p', 's'):
            v = int(tile.value)  # '1'〜'9' → 数値化
        else:
            # 字牌 'z' の場合 -> 'ton','nan','sha','pe','haku','hatsu','chun'
            # 好きな順番に割り当てる例: ton->1, nan->2, sha->3, pe->4, haku->5, hatsu->6, chun->7
            honor_map = {
                'ton': 1, 'nan': 2, 'sha': 3, 'pe': 4,
                'haku': 5, 'hatsu': 6, 'chun': 7
            }
            v = honor_map.get(tile.value, 0)  # 万が一想定外のvalueなら0などにしておく

        converted.append((suit_priority[s], v))

    # ここでソート
    converted.sort()

    # 返り値としては、この後の「刻子・順子判定」がやりやすい形にする。文字列で返してもOK
    return converted

def remove_two_tiles(original_list, idx1, idx2):
    """
    original_listから、指定した2つのインデックス要素を除去し、新しいリストを返す。
    original_list はタプルやTileのソート済み配列を想定。

    例:
        original_list = [(0,1),(0,1),(0,2),(0,3) ... ]
        remove_two_tiles(original_list, 0, 1)
        -> 上記で 0番目,1番目の要素を削除する新リストを返す

    注意:
      idx1,idx2の大小関係によってはpopの順番に注意。
      大きい方からpopしないと、先に小さい要素をpopしたとき
      後ろのindexがずれてしまう。
    """
    new_list = original_list[:]
    # idx1, idx2を大きい順に並べ替えて pop
    for idx in sorted([idx1, idx2], reverse=True):
        new_list.pop(idx)
    return new_list

def remove_three_tiles(original_list, val1, val2, val3):
    """
    original_list から val1, val2, val3 という値を1枚ずつ取り除いた新リストを返す。

    例えば:
      - 刻子: val1 == val2 == val3
      - 順子: val2 == val1+1, val3 == val1+2
    """
    new_list = original_list[:]

    # val1, val2, val3 をそれぞれ new_list から1回だけ削除
    for v in (val1, val2, val3):
        if v in new_list:
            new_list.remove(v)
        else:
            # v が見つからなければ取り除けない(エラー or そのままリターンなど)
            return None  # 取り除き失敗を示す

    return new_list

def is_sequence_possible(tiles_list):
    """
    tiles_list は [(suit_id, val), (suit_id, val), ...]
    先頭要素を first = tiles_list[0] として
    同じ suit_id で val, val+1, val+2 が含まれているかチェック
    """
    if not tiles_list:
        return False

    suit_id, val = tiles_list[0]

    # 字牌は順子不可なので suit_id==3 のときはFalse
    if suit_id == 3:
        return False

    return ((suit_id, val+1) in tiles_list) and ((suit_id, val+2) in tiles_list)

def remove_sequence(original_list, val1, val2, val3):
    """ original_list から (val1, val2, val3) を1回ずつ取り除いた新リストを返す """
    return remove_three_tiles(original_list, val1, val2, val3)


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
        matching = [t for t in tiles if t.is_same_tile(discard_tile)]
        if len(matching) >= 2:
            return [[matching[0], matching[1], discard_tile]]
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