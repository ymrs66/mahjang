# core/yaku_caliculator.py

from collections import Counter

def _counts_by_value(tiles):
#    """(suit,value) をキーにしたカウントを返す。Tileの同一性に依存しない。"""
    return Counter((t.suit, t.value) for t in tiles)


def calculate_yaku(concealed_hand, melds, win_tile, is_tsumo, player):
    """
    役計算関数（ドラなし版、簡易実装）
    :param concealed_hand: プレイヤーの隠し手牌（鳴いていない牌のリスト）
    :param melds: 鳴いた牌のリスト（例： [ [Tile,Tile,Tile], ... ] ）
    :param win_tile: 和了牌（Tileオブジェクト、使わない場合はNone）
    :param is_tsumo: ツモ和了ならTrue、ロンならFalse
    :param player: プレイヤーオブジェクト（リーチフラグなどの状態参照用）
    :return: (yaku_list, han)
    """
    yaku_list = []
    han = 0

    # 1) リーチ
    if player and player.is_reach:
        yaku_list.append("リーチ")
        han += 1

        # ダブルリーチ（例：オープンでなければダブルリーチ成立）
        if hasattr(player, "double_riichi") and player.double_riichi:
            yaku_list.append("ダブルリーチ")
            han += 1

        # 一発（リーチ直後に和了した場合）
        if hasattr(player, "ippatsu") and player.ippatsu:
            yaku_list.append("一発")
            han += 1

    # 2) ツモ（ツモ和了の場合のみ、ツモ役成立）
    if is_tsumo:
        yaku_list.append("ツモ")
        han += 1

    # 3) タンヤオ（従来通り）
    if is_tanyao(concealed_hand, melds):
        yaku_list.append("タンヤオ")
        han += 1

    # 4) ピンフ（ロンの場合のみ、かつ待ちが完全に両面待ちの場合）
    if (not is_tsumo) and is_pinfu(concealed_hand, melds, win_tile):
        yaku_list.append("ピンフ")
        han += 1

    # 5) イーペーコー
    if is_iipeikou(concealed_hand):
        yaku_list.append("イーペーコー")
        han += 1

    # 6) ホンイツ
    if is_honitsu(concealed_hand, melds):
        yaku_list.append("ホンイツ")
        # ※通常は門前なら3翻、鳴いていれば2翻（例）
        han += 3 if player.is_menzen else 2

    # 7) チンイツ
    if is_chinitsu(concealed_hand, melds):
        yaku_list.append("チンイツ")
        han += 6 if player.is_menzen else 5

    # 8) トイトイ
    if is_toitoi(concealed_hand, melds):
        yaku_list.append("トイトイ")
        han += 2

    # 三暗刻（隠し手牌内に3組以上の暗刻）
    if is_three_anko(concealed_hand):
        yaku_list.append("三暗刻")
        han += 1

    # チャンタ（全グループに端牌または字牌が含まれる）
    if is_chanta(concealed_hand, melds):
        yaku_list.append("チャンタ")
        han += 1

    # ジュンチャン（全グループに端牌が含まれ、字牌は一切なし）
    if is_junchan(concealed_hand, melds):
        yaku_list.append("ジュンチャン")
        han += 1

    # 三色同順（同じ数字の順子が３スートで成立）
    if is_sanshoku(concealed_hand, melds):
        yaku_list.append("三色同順")
        han += 1

    # 字牌暗刻（隠し手牌内に字牌の暗刻があれば）
    if is_honor_anko(concealed_hand):
        yaku_list.append("字牌暗刻")
        han += 1

    # 9) 役無し（何も役が成立しなかった場合）
    if not yaku_list:
        yaku_list.append("役無し")
        han = 0

    return yaku_list, han

# 各役の判定関数のサンプル実装例

def is_tanyao(concealed_hand, melds):
    """隠し手牌・鳴き牌ともに端牌・字牌がない場合にTrue"""
    for tile in concealed_hand:
        if is_terminal(tile) or is_honor(tile):
            return False
    for meld in melds:
        for tile in meld:
            if is_terminal(tile) or is_honor(tile):
                return False
    return True

def is_pinfu(concealed_hand, melds, win_tile):
    """
    ピンフ判定の簡易実装:
      - 門前である（meldsが空であること）
      - 手牌に刻子（同じ牌3枚以上）がなく、対子が1組のみ
      - 待ちが完全に両面待ち（待ち候補がwin_tileの前後両方にある）
    """
    # 1) 鳴いていればピンフではない
    if melds and len(melds) > 0:
        return False

    counts = _counts_by_value(concealed_hand)
    if any(c >= 3 for c in counts.values()):
        return False

    # 2) 対子の数をチェック
    pair_count = 0
    sorted_hand = sorted(concealed_hand, key=lambda t: (t.suit, int(t.value) if t.suit in ('m','p','s') else t.value))
    i = 0
    while i < len(sorted_hand) - 1:
        if sorted_hand[i].is_same_tile(sorted_hand[i+1]):
            pair_count += 1
            i += 2
        else:
            i += 1
    if pair_count != 1:
        return False

    # 3) 両面待ちのチェック（win_tileを基準に、前後の牌がどちらも欠けていないか）
    return is_ryanmen_wait(concealed_hand, win_tile)

def is_ryanmen_wait(concealed_hand, win_tile):
    """
    両面待ちかどうかを判定する簡易例:
      例えば、win_tileが5の場合、4と6が待ち候補にあるかどうかをチェックする
      ※実際には、手牌全体の待ち候補分析が必要になりますが、ここではサンプルとして
    """
    if win_tile and win_tile.suit in ('m', 'p', 's'):
        val = int(win_tile.value)
        # 端牌は両面待ちにならない
        if val == 1 or val == 9:
            return False
        # 簡単のため、両面待ちならTrue（詳細な判定は要実装）
        return True
    return False

def is_iipeikou(concealed_hand):
    """
    イーペーコー判定の簡易例:
      - 手牌内に同一の順子が2組ある場合に成立
      ※ 実際には順子の並びや重複を詳細にチェックする必要があります。
    """
    # サンプルとして常にFalseを返す（実装は要検討）
    return False

def is_honitsu(concealed_hand, melds):
    """
    ホンイツ判定の簡易例:
      - 手牌が1つの数牌のスートと字牌のみで構成されている場合に成立
    """
    suits = set()
    for tile in concealed_hand:
        suits.add(tile.suit)
    for meld in melds:
        for tile in meld:
            suits.add(tile.suit)
    # ホンイツなら数牌のスートが1種類のみ（字牌は複数あってもOK）
    non_honor = [s for s in suits if s != 'z']
    return len(non_honor) == 1

def is_chinitsu(concealed_hand, melds):
    """
    チンイツ判定の簡易例:
      - 手牌と鳴き牌が全て同一の数牌スートで構成されている場合に成立
    """
    suits = set()
    for tile in concealed_hand:
        suits.add(tile.suit)
    for meld in melds:
        for tile in meld:
            suits.add(tile.suit)
    # チンイツなら数牌のみで1種類
    return suits.issubset({'m'}) or suits.issubset({'p'}) or suits.issubset({'s'})

def is_toitoi(concealed_hand, melds):
    """
    トイトイ判定の簡易例:
      - 全ての鳴き牌が刻子またはカンであること
      ※ 隠し手牌に順子が含まれている場合は成立しない
    """
    # ここでは、メルドが存在する場合に、全てのメルドが3枚または4枚の同一牌であればトイトイとする
    return False # 中途半端な実装のためひとまずFalse
    for meld in melds:
        if len(meld) not in (3, 4):
            return False
        # 3枚、4枚とも全て同じ牌であることは前提とする
    # また、隠し手牌も順子になっていない（対子だけ、または単一の牌）と仮定
    return True

def is_three_anko(concealed_hand):
    """隠し手牌内で、同一牌が3枚以上あるものをカウントし、3組以上なら三暗刻とする"""
    counts = _counts_by_value(concealed_hand)
    anko_count = sum(1 for _, c in counts.items() if c >= 3)
    return anko_count >= 3

def is_chanta(concealed_hand, melds):
    """
    簡易版チャンタ判定：
    ※各グループ（隠し手牌＋鳴き牌）は、端牌（1または9）または字牌を含むとする。
    ここでは、全体の牌（隠し手牌と鳴き牌を合わせたもの）に1枚以上の端牌または字牌があれば成立とする（大雑把な実装）。
    """
    return False #実装が中途半端なためひとまずFalse
    all_tiles = concealed_hand[:]
    for meld in melds:
        all_tiles.extend(meld)
    # 少なくとも1枚の端牌または字牌があるならチャンタの可能性あり
    for tile in all_tiles:
        if is_terminal(tile) or is_honor(tile):
            return True
    return False

def is_junchan(concealed_hand, melds):
    """
    簡易版ジュンチャン判定：
    ・全体の牌に字牌が含まれず、かつ必ず端牌が含まれている
    ※実際は各グループごとに判定する必要がありますが、ここでは全体でチェックする簡易実装とする。
    """
    return False #実装が中途半端なためひとまずFalse
    all_tiles = concealed_hand[:]
    for meld in melds:
        all_tiles.extend(meld)
    # 字牌が含まれていたらジュンチャンではない
    if any(is_honor(tile) for tile in all_tiles):
        return False
    # 端牌が存在するか
    return any(is_terminal(tile) for tile in all_tiles)

def is_sanshoku(concealed_hand, melds):
    """
    簡易版三色同順判定：
    鳴き牌の中から順子（3枚組で連続するもの）を抽出し、
    同じ数列が三種類のスートに渡って存在すれば成立とする。
    """
    return False #実装が中途半端なためひとまずFalse
    sequences = []
    # 鳴き牌から順子を抽出
    for meld in melds:
        if len(meld) == 3:
            sorted_meld = sorted(meld, key=lambda t: (t.suit, int(t.value) if t.suit in ('m','p','s') else 0))
            if sorted_meld[0].suit in ('m', 'p', 's'):
                try:
                    if int(sorted_meld[1].value) == int(sorted_meld[0].value) + 1 and \
                       int(sorted_meld[2].value) == int(sorted_meld[0].value) + 2:
                        sequences.append((sorted_meld[0].suit, int(sorted_meld[0].value)))
                except Exception:
                    continue
    from collections import defaultdict
    seq_dict = defaultdict(set)
    for suit, num in sequences:
        seq_dict[num].add(suit)
    for num, suits in seq_dict.items():
        if len(suits) >= 3:
            return True
    return False

def is_honor_anko(concealed_hand):
    """隠し手牌内に、字牌の暗刻（3枚以上）があればTrue"""
    counts = _counts_by_value(concealed_hand)
    for (suit, _), c in counts.items():
        if suit == 'z' and c >= 3:
            return True
    return False

# 以下、既存のis_terminal, is_honorはそのままでOK
def is_terminal(tile):
    if tile.suit in ('m', 'p', 's'):
        return int(tile.value) in (1, 9)
    return False

def is_honor(tile):
    return tile.suit == 'z'
