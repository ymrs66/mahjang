##game.py
import random
from core.tile import Tile
from core.hand import Hand
from ai.ai_player import AIPlayer
from core.constants import *
from core.player import Player

class Game:
    def __init__(self):
        self.tile_cache = {}  # キャッシュ用辞書（未使用であれば削除検討）
        self.wall = self.generate_wall()  # 山牌
        self.players = [Player(), AIPlayer(1)]  # プレイヤー(0)とAI(1)
        self.discards = [[], []]  # プレイヤーの捨て牌[0]とAIの捨て牌[1]
        self.can_pon = False  # ポン可能フラグ
        self.can_chi = False  # チー可能フラグ
        self.can_kan = False  # カン可能フラグ
        self.target_tile = None  # ポン/チー対象の牌
        self.chi_candidates = []  # チー候補のリストを初期化
        self.kan_candidates = []  # カン候補のリストを初期化

    def is_game_over(self):
        """
        ゲーム終了条件を判定する。
        山牌がなくなった場合にTrueを返す。
        """
        return len(self.wall) == 0

    def generate_wall(self):
        """麻雀の山を生成する"""
        wall = []
        for _ in range(4):  # 各牌を4回追加
            for suit in SUITS:
                for value in range(1, 10):
                    wall.append(Tile(suit, str(value), TILE_IMAGE_PATH.format(value=value, suit=suit)))
            for honor in HONORS:
                # 字牌の画像パスには 'z' を除く
                wall.append(Tile('z', honor, TILE_IMAGE_PATH.format(value=honor, suit='')))
        return wall


    def shuffle_wall(self):
        """山牌をシャッフル"""
        random.shuffle(self.wall)

    def draw_tile(self, player_id):
        if self.wall:
            tile = self.wall.pop()
            # 捨て牌リストとの重複チェックなどはそのまま
            # ただし、print("プレイヤーがツモ") は書かない
            return tile
        else:
            return None

    def deal_initial_hand(self):
        """初期の手牌を配る"""
        for _ in range(13):
            self.players[0].add_tile(self.draw_tile(0))  # プレイヤー
            self.players[1].add_tile(self.draw_tile(1))  # AI
        print(f"初期配布完了: プレイヤー: {len(self.players[0].tiles)}枚,\
            AI: {len(self.players[1].hand.tiles)}枚")

    def get_available_actions(self, player_id, discard_tile):
        """
        他家の捨て牌 (discard_tile) に対して、
        ポン / チー / カン（明槓 or 加槓）の可否を判定し、
        さらに手牌だけで暗槓ができるかもチェックして、まとめて返す。
        """
        actions = []

        # ポン判定
        pon_candidates = self.check_pon(player_id, discard_tile)
        if pon_candidates:
            actions.append("ポン")

        # チー判定
        chi_candidates = self.check_chi(player_id, discard_tile)
        if chi_candidates:
            actions.append("チー")

        # 明槓 or 加槓 の判定（discard_tile がある前提）
        # → check_kan(...) に discard_tile を渡して判定
        kan_candidates_from_discard = self.check_kan(player_id, discard_tile)
        # check_kan で self.can_kan が設定される
        # もしここで can_kan == True なら "カン" 候補がある

        # ---- ここが大事: 暗槓 の判定 ----
        # tile=None を指定して、手牌のみで4枚揃いがあるかチェック
        kan_candidates_dark = self.check_kan(player_id, None)
        # 上の呼び出しでも self.can_kan が True になる可能性あり

        # もし check_kan のいずれかで self.can_kan == True になったら "カン" を追加
        if self.can_kan:
            # 「重複してカンが2回分出る」のを防ぎたいので、1回だけ "カン" を追加
            actions.append("カン")

        return actions


    def discard_tile(self, tile, player_id):
        if player_id == 0:  # プレイヤーの場合
            print(f"手牌から捨てます: {tile}")
            self.players[0].discard_tile(tile)
            self.discards[0].append(tile)

            # ポン・チー状態のリセット
            self.can_pon = False
            self.can_chi = False
            self.target_tile = None

        else:  # AIの場合
            discarded_tile = self.players[1].discard_tile()
            if discarded_tile:
                self.discards[1].append(discarded_tile)
                print(f"AIが捨てた牌: {discarded_tile}")
            else:
                print("エラー: AIが捨て牌を選択できませんでした！")


    def check_pon(self, player_id, discard_tile):
        if discard_tile is None:
            return []

        # プレイヤーでなければポンしない想定なら
        #if player_id != 0:
        #    return []

        hand = self.players[player_id].tiles
        count = sum(1 for t in hand if t.is_same_tile(discard_tile))

        # 実際のポン候補（2枚+捨て牌）をまとめたリスト
        pon_candidates = []
        if count >= 2:
            # 2枚 + discard_tile をひとまとめにした候補を作る
            # 例: [pon_tile, pon_tile, discard_tile]
            pon_candidates.append([discard_tile, discard_tile, discard_tile])  # 仮にこう書く
            # あるいは、実際には手牌に同じタイルオブジェクトが2枚分あるので取り出してリスト化
            # ...（省略）

            self.can_pon = True
            self.pon_candidates = pon_candidates
            self.target_tile = discard_tile
            print(f"[ポン可能] {discard_tile} でポンが可能, pon_candidates={pon_candidates}")
        else:
            self.can_pon = False
            self.pon_candidates = []
            self.target_tile = None
        return pon_candidates

    def process_pon(self, player_id, state):
        """
        ポン処理を実行する。
        """
        if not self.can_pon or self.target_tile is None:
            return

        # 手牌からポン対象の2枚を取得
        player_hand = self.players[player_id].tiles
        pon_tiles = [t for t in player_hand if t.is_same_tile(self.target_tile)][:2]

        if len(pon_tiles) < 2:
            print("ポン対象の牌が手牌に不足しています")
            return

        # 手牌からポン対象の2枚を削除
        for tile in pon_tiles:
            self.players[player_id].remove_tile(tile)

        # 捨て牌から対象牌を削除
        self.discards[1] = [t for t in self.discards[1] if not t.is_same_tile(self.target_tile)]

        # ポンした牌を記録
        self.players[player_id].pons.append(pon_tiles + [self.target_tile])

        print(f"ポン成功: {pon_tiles + [self.target_tile]}")
        self.can_pon = False
        self.target_tile = None

        # プレイヤーの捨てるフェーズに移行
        state.transition_to(PLAYER_DISCARD_PHASE)

# game.py 内の check_chi を差し替え/修正

    def check_chi(self, player_id, discard_tile):
        """
        チー可能な牌の組み合わせをチェック (重複牌も正しく扱う)
        """
        player_hand = self.players[player_id].tiles
        discard_suit = discard_tile.suit

        print(f"チー判定開始: プレイヤー{player_id}, 捨て牌: {discard_tile}")

        # 捨て牌が数牌でない場合はチー不可
        if discard_suit not in ["m", "p", "s"]:
            print("チー不可: 捨て牌が数牌ではありません")
            return []

        try:
            discard_value = int(discard_tile.value)  # 数牌の場合、値を整数型に変換
        except ValueError:
            print("チー不可: 捨て牌の値が整数に変換できません")
            return []

        # --- ここから修正 ---
        from collections import Counter

        # 同スーツの牌のみカウントする
        # （捨て牌と同じスーツに限定）
        same_suit_values = [int(t.value) for t in player_hand if t.suit == discard_suit]
        tile_counter = Counter(same_suit_values)

        chi_candidates = []
        chi_patterns = [
            [-2, -1],  # 例: [discard_value-2, discard_value-1, discard_value]
            [-1, 1],   # [discard_value-1, discard_value, discard_value+1]
            [1, 2]     # [discard_value, discard_value+1, discard_value+2]
        ]

        for offsets in chi_patterns:
            needed_values = [discard_value + offset for offset in offsets]
            print(f"必要な値: {needed_values} (オフセット: {offsets})")

            # 範囲外(1～9)の値が含まれる場合は即スキップ
            if any(v < 1 or v > 9 for v in needed_values):
                continue

            # 全ての needed_value が手牌中に1枚以上あるかチェック
            can_form = True
            for val in needed_values:
                if tile_counter[val] < 1:
                    can_form = False
                    break

            # もし全部揃っていればチー可能
            if can_form:
                # 実際に 2 枚ピックアップし、捨て牌を加える
                candidate_tiles = []
                # 順序は (小さい順 → 大きい順)、最後に discard_tile は必ず入れるが、
                # ここでは分かりやすく 2枚だけピックアップ
                used_temp = Counter()  # どの値を何枚使ったか

                for val in needed_values:
                    # 同じ val の牌の中からまだ使っていない牌を1枚ピックアップ
                    # (同値が複数ある場合でも1枚は必ず取れる想定)
                    for t in player_hand:
                        if t.suit == discard_suit and int(t.value) == val and used_temp[val] < tile_counter[val]:
                            candidate_tiles.append(t)
                            used_temp[val] += 1
                            break

                # candidate_tiles 2枚 + discard_tile で3枚構成
                new_sequence = candidate_tiles + [discard_tile]
                chi_candidates.append(new_sequence)
                print(f"チー候補に追加: {new_sequence}")

        if chi_candidates:
            self.can_chi = True
            self.target_tile = discard_tile
            self.chi_candidates = chi_candidates
        else:
            self.can_chi = False
            self.chi_candidates = []

        print(f"最終的なチー候補: {chi_candidates}")
        return chi_candidates


    def process_chi(self, player_id, chosen_sequence,state):
        """
        チー処理を実行する。
        """
        if self.target_tile is None:
            print("エラー: target_tile が None です。")
            return

        print(f"チー処理開始: プレイヤー{player_id}, 選択された順子: {chosen_sequence}")
        player_hand = self.players[player_id].tiles  # プレイヤーの手牌を取得

        # 捨て牌を除外した順子部分を取得
        sequence_without_discard = [tile for tile in chosen_sequence if not (
            tile.suit == self.target_tile.suit and tile.value == self.target_tile.value
        )]

        # 手牌に必要な牌が揃っているか確認
        if not all(tile in player_hand for tile in sequence_without_discard):
            print(f"エラー: {sequence_without_discard} の一部が手牌に存在しません")
            return

        # チー牌を手牌から削除
        for tile in sequence_without_discard:
            self.players[player_id].remove_tile(tile)

        # 捨て牌を捨て牌リストから削除
        if self.target_tile in self.discards[1]:  # AIが捨てた牌から削除
            self.discards[1].remove(self.target_tile)

        # チーした牌を記録
        self.players[player_id].chis.append(chosen_sequence)  # 順子をチーリストに追加

        print(f"チー成功: {chosen_sequence}")
        self.can_chi = False  # チー状態をリセット
        self.target_tile = None  # ターゲット牌をリセット

        # プレイヤーの捨てるフェーズに移行	
        state.transition_to(PLAYER_DISCARD_PHASE) # プレイヤーターン（捨てるフェーズ）


    def check_kan(self, player_id, tile=None):
        """
        カンが可能か判定する。
        player_id: プレイヤーID
        tile: 他のプレイヤーが捨てた牌（明槓用）。Noneの場合は手牌を調べる（暗槓/加槓）。
        """
        hand = self.players[player_id].tiles
        pons = self.players[player_id].pons  # ポンした牌のリスト
        kan_candidates = []

        def count_tile_in_hand(target_tile):
            """手牌内で指定された牌の数を数える"""
            return sum(1 for t in hand if t.is_same_tile(target_tile))  # is_same_tile を使用

        # 暗槓のチェック
        if tile is None:
            for t in hand:
                if count_tile_in_hand(t) == 4 and t not in kan_candidates:
                    kan_candidates.append(t)

        # 明槓のチェック
        elif count_tile_in_hand(tile) == 3:
            kan_candidates.append(tile)

        # 加槓のチェック
        for pon_set in pons:
            # pon_set が有効か確認し、tile との一致をチェック
            if pon_set and len(pon_set) == 3 and tile and pon_set[0].is_same_tile(tile):  # is_same_tile を使用
                kan_candidates.append(tile)

        if kan_candidates:
            self.can_kan = True
            self.kan_candidates = kan_candidates
        else:
            self.can_kan = False
            self.kan_candidates = []
        return kan_candidates
    
    def process_kan(self, player_id, tile, state, kan_type):
        """
        カンの処理を実行する。
        player_id: プレイヤーID
        tile: カン対象の牌
        kan_type: '暗槓', '明槓', '加槓'のいずれか
        """
        if kan_type == '暗槓':
            # 手牌から4枚を削除し、カンリストに追加
            self.players[player_id].tiles = [t for t in self.players[player_id].tiles if not t.is_same_tile(tile)]
            self.players[player_id].kans.append([tile] * 4)
            print(f"暗槓成功: {tile}")

        elif kan_type == '明槓':
            # 手牌から3枚を削除し、捨て牌を合わせてカンリストに追加
            self.players[player_id].tiles = [t for t in self.players[player_id].tiles if not t.is_same_tile(tile)]
            self.players[player_id].kans.append([tile] * 4)
            self.discards[1] = [d for d in self.discards[1] if not d.is_same_tile(tile)]
            print(f"明槓成功: {tile}")

        elif kan_type == '加槓':
        # ポンから対象のセットを探してカンに移動
            for pon_set in self.players[player_id].pons:
                if self.is_same_tile(pon_set[0], tile):
                    self.players[player_id].pons.remove(pon_set)
                    self.players[player_id].kans.append(pon_set + [tile])
                    self.players[player_id].tiles.remove(tile)  # 手牌から1枚削除
                    print(f"加槓成功: {pon_set + [tile]}")
                    break

        # **嶺上牌のツモ処理を追加**
        new_tile = self.wall.pop() if self.wall else None
        if new_tile:
            self.players[player_id].add_tile(new_tile)
            print(f"嶺上牌をツモ: {new_tile}")
        else:
            print("山牌がありません！ゲーム終了です。")

    def determine_kan_type(self, player_id, tile):
        """
        どの種類のカンが可能かを判定する。
        :param player_id: プレイヤーID
        :param tile: カン対象の牌
        :return: "暗槓", "明槓", "加槓" のいずれか
        """
        player_hand = self.players[player_id].tiles
        player_pons = self.players[player_id].pons

        # 暗槓（手牌に4枚揃っている）
        if player_hand.count(tile) == 4:
            return "暗槓"

        # 明槓（捨て牌を含めて4枚になる）
        if self.target_tile and self.target_tile.is_same_tile(tile):
            discard_count = sum(1 for d in self.discards[1] if d.is_same_tile(tile))  # AIの捨て牌からカウント
            if discard_count == 1 and player_hand.count(tile) == 3:
                return "明槓"

        # 加槓（ポン済みの牌と同じ牌が1枚手牌にある）
        for pon_set in player_pons:
            if pon_set and len(pon_set) == 3 and pon_set[0].is_same_tile(tile) and player_hand.count(tile) == 1:
                return "加槓"

        return None  # カン不可