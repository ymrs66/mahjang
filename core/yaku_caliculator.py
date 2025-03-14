# file: core/yaku_caliculator.py

def calculate_yaku(concealed_hand, melds, win_tile, is_tsumo, player):
    """
    役計算関数（ドラなし版）
    :param concealed_hand: 手牌（鳴いていない部分）リスト
    :param melds: 鳴いた牌のリスト (pon/chikanなど) [ [Tile,Tile,Tile], ... ]
    :param win_tile: 和了牌(Tile) / 使わない場合はNone
    :param is_tsumo: ツモ和了ならTrue、ロンならFalse
    :param is_reach: リーチ状態ならTrue、デフォルトはFalse(オプション)

    戻り値: (yaku_list, han)
      yaku_list: 役名のリスト e.g. ["リーチ","ツモ","タンヤオ",...]
      han: 合計翻数(int)
    """
    yaku_list = []
    han = 0

    # --- 1) リーチがあれば1翻 ---
    if player and player.is_reach:
        yaku_list.append("リーチ")
        han += 1

    # --- 2) ツモがあれば1翻 ---
    #     (要件: ツモとピンフは両立させない)
    if is_tsumo:
        yaku_list.append("ツモ")
        han += 1

    # --- 3) タンヤオ ---
    #    (従来通りの判定)
    if is_tanyao(concealed_hand, melds):
        yaku_list.append("タンヤオ")
        han += 1

    # --- 4) ピンフ ---
    #    ツモと同時成立はしない(両立NG)ので、 is_tsumo=Falseのときだけ判定
    #    門前 ＋ 刻子(暗刻)がなく かつ 1つだけ対子＋残りが順子 ならピンフとする
    #    (簡易チェックの例: 下記 is_pinfu 参照)
    if (not is_tsumo) and is_pinfu(concealed_hand, melds):
        yaku_list.append("ピンフ")
        han += 1

    return yaku_list, han


def is_terminal(tile):
    """ 数牌であって1または9なら True """
    if tile.suit in ('m', 'p', 's'):
        return int(tile.value) in (1, 9)
    return False


def is_honor(tile):
    """ 字牌なら True """
    return tile.suit == 'z'


def is_tanyao(concealed_hand, melds):
    """
    タンヤオ判定: 牌が1,9,字牌を含まないならTrue
      鳴き牌(melds) にも端牌や字牌が無いことを確認。
    """
    # -- 隠し手牌チェック --
    for tile in concealed_hand:
        if is_terminal(tile) or is_honor(tile):
            return False

    # -- 鳴き牌チェック --
    for meld in melds:
        for tile in meld:
            if is_terminal(tile) or is_honor(tile):
                return False

    return True


def is_pinfu(concealed_hand, melds):
    """
    簡易版のピンフ判定:
      1) 門前 (meldsが空)
      2) 手牌の中に刻子(= 同じ牌3枚)がない
      3) ちょうど1つだけ対子があり、残りは順子になりうる
         (細かい順子チェックは省略し、暗刻がない前提で簡易的に返す例など)
    """
    # 1) 鳴いていればピンフでない
    if melds and len(melds) > 0:
        return False

    # 2) Concealed handに同じ牌が3枚以上あるとピンフ不可
    from collections import Counter
    counts = Counter(concealed_hand)
    if any(counts[t] >= 3 for t in counts):
        return False

    # 3) 一対子 + 残り順子 の簡易判定
    #    ここでは “対子が1組のみあればOK” くらいの非常に大雑把な判定
    pair_count = 0
    # ソートして同じ牌が2枚並んでいるかを探す
    sorted_hand = sorted(concealed_hand, key=lambda t: (t.suit, int(t.value) if t.suit in ('m','p','s') else t.value))
    i = 0
    while i < len(sorted_hand) - 1:
        if sorted_hand[i].is_same_tile(sorted_hand[i+1]):
            pair_count += 1
            i += 2
        else:
            i += 1

    # ピンフを満たすには pair_count=1 が望ましい
    if pair_count != 1:
        return False

    return True
