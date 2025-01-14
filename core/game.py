##game.py
import random
from core.tile import Tile
from core.hand import Hand
from ai.ai_player import AIPlayer
from core.constants import *

class Game:
    def __init__(self):
        self.tile_cache = {}  # キャッシュ用辞書（未使用であれば削除検討）
        self.wall = self.generate_wall()  # 山牌
        self.players = [Hand(), AIPlayer(1)]  # プレイヤー(0)とAI(1)
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
        """指定されたプレイヤーが山から1枚ツモる"""
        if self.wall:
            tile = self.wall.pop()
            # 捨て牌リストにツモ牌が含まれていないか確認
            if tile in self.discards[player_id]:
                print(f"警告: ツモ牌 {tile} は既に捨て牌リストに存在します")
                return None

            if player_id == 0:  # プレイヤーの場合
                self.tsumo_tile = tile  # ツモ牌を記録
                print(f"プレイヤーがツモ: {tile}")
            else:
                print(f"AIがツモ: {tile}")
            return tile
        else:
            print("山が空です！")
            return None

    def deal_initial_hand(self):
        """初期の手牌を配る"""
        for _ in range(13):
            self.players[0].add_tile(self.draw_tile(0))  # プレイヤー
            self.players[1].add_tile(self.draw_tile(1))  # AI
        print(f"初期配布完了: プレイヤー: {len(self.players[0].tiles)}枚,\
            AI: {len(self.players[1].hand.tiles)}枚")

    def discard_tile(self, tile, player_id):
        if player_id == 0:  # プレイヤーの場合
            if tile == self.tsumo_tile:
                print(f"ツモ牌を捨てます: {tile}")
                self.discards[0].append(tile)
                self.tsumo_tile = None
            else:
                print(f"手牌から捨てます: {tile}")
                self.players[0].remove_tile(tile)
                self.discards[0].append(tile)

                # ポン・チー状態のリセット
                self.can_pon = False
                self.can_chi = False
                self.target_tile = None

            # ターンをAIに移行
            self.current_turn = AI_TURN_PHASE  # AIのターン

        else:  # AIの場合
            discarded_tile = self.players[1].discard_tile()
            if discarded_tile:
                self.discards[1].append(discarded_tile)
                print(f"AIが捨てた牌: {discarded_tile}")
            else:
                print("エラー: AIが捨て牌を選択できませんでした！")

            # ターンをプレイヤーのツモフェーズに移行
            state.transition_to(PLAYER_DRAW_PHASE)  # プレイヤーのツモフェーズ

    def check_pon(self, player_id, tile):
        """
        ポンが可能か判定する。
        """
        if tile is None or player_id != 0:  # 現在はプレイヤーのみ実装
            return False
        hand = self.players[player_id].tiles
        count = sum(1 for t in hand if t.is_same_tile(tile))  # is_same_tile を使用
        if count >= 2:
            self.can_pon = True
            self.target_tile = tile
            return True
        else:
            self.can_pon = False
            self.target_tile = None
            return False

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
            self.players[player_id].tiles.remove(tile)

        # 捨て牌から対象牌を削除
        self.discards[1] = [t for t in self.discards[1] if not t.is_same_tile(self.target_tile)]

        # ポンした牌を記録
        self.players[player_id].pons.append(pon_tiles + [self.target_tile])

        print(f"ポン成功: {pon_tiles + [self.target_tile]}")
        self.can_pon = False
        self.target_tile = None

        # プレイヤーの捨てるフェーズに移行
        state.transition_to(PLAYER_DISCARD_PHASE)

    def check_chi(self, player_id, discard_tile):
        """
        チー可能な牌の組み合わせをチェック
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

        chi_candidates = []
        chi_patterns = [
            [-2, -1],  # 捨て牌の前に2つ連続
            [-1, 1],   # 捨て牌を中心に前後1つずつ
            [1, 2]     # 捨て牌の後に2つ連続
        ]

        for offsets in chi_patterns:
            needed_values = [discard_value + offset for offset in offsets]
            print(f"必要な値: {needed_values} (オフセット: {offsets})")

            # 必要な値が手牌に揃っているか確認
            candidate_tiles = []
            used_values = set()

            for tile in player_hand:
                if (
                    tile.suit == discard_suit 
                    and int(tile.value) in needed_values
                    and (int(tile.value), id(tile)) not in used_values  # 値とIDでユニーク性を保証
                ):
                    candidate_tiles.append(tile)
                    used_values.add((int(tile.value), id(tile)))

            # 候補が2枚以上揃っている場合に順子を形成
            if len(candidate_tiles) >= 2:
                candidate_values = sorted([int(tile.value) for tile in candidate_tiles] + [discard_value])
                if candidate_values == list(range(min(candidate_values), max(candidate_values) + 1)):
                    # 必要な2枚を抽出し、捨て牌を最後に追加
                    required_tiles = candidate_tiles[:2]
                    required_tiles.append(discard_tile)
                    chi_candidates.append(required_tiles)
                    print(f"チー候補に追加: {required_tiles}")

        if chi_candidates:
            self.target_tile = discard_tile  # ターゲット牌を設定

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

        print(f"カン候補: {kan_candidates}")
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
            # ポンした牌に1枚を追加し、カンリストに移動
            for pon_set in self.players[player_id].pons:
                if pon_set[0].is_same_tile(tile):
                    self.players[player_id].pons.remove(pon_set)
                    self.players[player_id].kans.append(pon_set + [tile])
                    self.players[player_id].tiles = [t for t in self.players[player_id].tiles if not t.is_same_tile(tile)]
                    break
            print(f"加槓成功: {tile}")

        # **嶺上牌のツモ処理を追加**
        new_tile = self.wall.pop() if self.wall else None
        if new_tile:
            self.players[player_id].add_tile(new_tile)
            print(f"嶺上牌をツモ: {new_tile}")
        else:
            print("山牌がありません！ゲーム終了です。")