# File: mahjang\core\game.py

import random
from core.tile import Tile
from core.hand import Hand
from ai.ai_player import AIPlayer
from core.player import Player
from core.constants import *
# meld_checker.py をインポート
from meld_checker import MeldChecker

class Game:
    def __init__(self):
        self.tile_cache = {}
        self.wall = self.generate_wall()
        self.players = [Player(), AIPlayer(1)]
        self.discards = [[], []]

        # ===============================
        # フラグや候補 (ポン／チー／カン) 周りを簡潔化
        # meld_enabled と meld_candidates に一本化
        self.target_tile = None
        self.meld_candidates = {
            "pon": [],
            "chi": [],
            "kan": []
        }
        self.meld_enabled = {
            "pon": False,
            "chi": False,
            "kan": False
        }

    def generate_wall(self):
        wall = []
        for _ in range(4):
            for suit in SUITS:
                for value in range(1, 10):
                    wall.append(Tile(suit, str(value), TILE_IMAGE_PATH.format(value=value, suit=suit)))
            for honor in HONORS:
                wall.append(Tile('z', honor, TILE_IMAGE_PATH.format(value=honor, suit='')))
        return wall

    def shuffle_wall(self):
        random.shuffle(self.wall)

    def draw_tile(self, player_id):
        if self.wall:
            return self.wall.pop()
        else:
            return None

    def deal_initial_hand(self):
        for _ in range(13):
            self.players[0].add_tile(self.draw_tile(0))
            self.players[1].add_tile(self.draw_tile(1))
        print(f"初期配布完了: プレイヤー: {len(self.players[0].tiles)}枚, "
              f"AI: {len(self.players[1].tiles)}枚")

    def is_game_over(self):
        return len(self.wall) == 0

    # ============================================
    # まとめて(ポン/チー/カン)判定し、meld_candidates と meld_enabled を更新
    # ============================================
    def check_all_melds_in_game(self, player_id, discard_tile):
        tiles = self.players[player_id].tiles
        pons = self.players[player_id].pons

        result = MeldChecker.check_all_melds(tiles, pons, discard_tile)

        self.meld_candidates = {
            "pon": result["pon_candidates"],
            "chi": result["chi_candidates"],
            "kan": result["kan_candidates"],
        }
        self.meld_enabled = {
            key: (len(self.meld_candidates[key]) > 0)
            for key in ["pon", "chi", "kan"]
        }

        # target_tile は discard_tile を共有
        if discard_tile is not None:
            self.target_tile = discard_tile

        return result

    def get_available_actions(self, player_id, discard_tile):
        """
        ポン/チー/カン判定をまとめて呼び出し、
        実行可能なアクション名をリストで返す。
        """
        self.check_all_melds_in_game(player_id, discard_tile)

        actions = []
        if self.meld_enabled["pon"]:
            actions.append("ポン")
        if self.meld_enabled["chi"]:
            actions.append("チー")
        if self.meld_enabled["kan"]:
            actions.append("カン")
        return actions

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
        # たとえば「target_tile == tile」かつ「手札に3枚同じ牌がある」などをチェック
        if self.target_tile and self.target_tile.is_same_tile(tile):
            discard_count = sum(1 for d in self.discards[1] if d.is_same_tile(tile))  # AIの捨て牌から枚数カウント
            if discard_count == 1 and player_hand.count(tile) == 3:
                return "明槓"

        # 加槓（ポン済みの牌と同じ牌が1枚手牌にある）
        # たとえば「既に pons にある [tile,tile,tile] が存在し、手札に tile が1枚ある」等
        for pon_set in player_pons:
            if len(pon_set) == 3 and pon_set[0].is_same_tile(tile):
                if player_hand.count(tile) == 1:
                    return "加槓"

        return None  # カン不可

    def discard_tile(self, tile, player_id):
        if player_id == 0:
            print(f"手牌から捨てます: {tile}")
            self.players[0].discard_tile(tile)
            self.discards[0].append(tile)

            # ================================
            # meld_enabled / target_tile のリセット
            # ================================
            for k in self.meld_enabled:
                self.meld_enabled[k] = False
            self.target_tile = None

        else:
            discarded_tile = self.players[1].discard_tile()
            if discarded_tile:
                self.discards[1].append(discarded_tile)
                print(f"AIが捨てた牌: {discarded_tile}")
            else:
                print("エラー: AIが捨て牌を選択できませんでした！")

    # ============================================
    # 共通メルド処理
    # ============================================
    def process_meld(self, player_id, meld_type, tiles_to_remove, state):
        """
        汎用的なメルド実行処理
          - meld_type: "pon" / "chi" / "kan" のいずれか
          - tiles_to_remove: 手牌から除去する牌リスト ([pon対象の2枚], [chi対象の2枚], など)
        """

        # (1) 手札から除去
        for t in tiles_to_remove:
            self.players[player_id].remove_tile(t)

        # (2) 捨て牌から1枚除去（target_tile がある場合のみ）
        if self.target_tile:
            self.discards[1] = [t for t in self.discards[1] if not t.is_same_tile(self.target_tile)]

        # (3) メルド先に追加
        if meld_type == "pon":
            self.players[player_id].pons.append(tiles_to_remove + [self.target_tile])
        elif meld_type == "chi":
            self.players[player_id].chis.append(tiles_to_remove + [self.target_tile])
        elif meld_type == "kan":
            self.players[player_id].kans.append(tiles_to_remove + [self.target_tile])
        else:
            print(f"[警告] 不明なmeld_typeです: {meld_type}")

        # (4) ログやフラグのリセット
        print(f"{meld_type}成功: {tiles_to_remove + [self.target_tile]}")
        self.meld_enabled[meld_type] = False  # can_pon / can_chi / can_kan の代わり
        self.target_tile = None

        # (5) フェーズ遷移
        state.waiting_for_player_discard = False
        state.transition_to(PLAYER_DISCARD_PHASE)

    # ============================================
    # 各メルド種別ごとの実行メソッド
    # ============================================
    def process_pon(self, player_id, state):
        # meld_enabled["pon"] / meld_candidates["pon"] などを参照
        if not self.meld_enabled["pon"] or (self.target_tile is None):
            return

        # pon候補から最初のセットを使う例 (実際には複数候補があるかもしれない)
        pon_sets = self.meld_candidates["pon"]
        if not pon_sets:
            print("[エラー] pon候補がありません")
            return

        # 今回は最初の pon_sets[0] を使う例
        # MeldChecker.can_pon(...) が [[discard_tile, discard_tile, discard_tile]] を返すなら、
        # 手札ぶん(=2枚) は pon_set[:-1] になるかもしれない。
        pon_set = pon_sets[0]
        # 例えば discard_tile 3枚全部同じtileオブジェクトなら → 先頭2枚を "手札用" とみなす
        tiles_to_remove = pon_set[:-1]

        self.process_meld(player_id, "pon", tiles_to_remove, state)

    def process_chi(self, player_id, chosen_sequence, state):
        if not self.meld_enabled["chi"] or (self.target_tile is None):
            return

        # chosen_sequence から discard_tile 分を除外した2枚を取り除く
        seq_without_discard = [t for t in chosen_sequence if not t.is_same_tile(self.target_tile)]
        self.process_meld(player_id, "chi", seq_without_discard, state)

    def process_kan(self, player_id, tile, state):
        """
        カンの処理 (暗槓, 明槓, 加槓)。
        """
        # 1) どのカンか判定
        kan_type = self.determine_kan_type(player_id, tile)
        if kan_type is None:
            print("[エラー] カンできない状態またはkan_type不明です")
            return

        # 2) 除去すべき牌を確定
        if kan_type == "暗槓":
            # 手牌中に tile が4枚ある
            kan_tiles = [tile]*4
        elif kan_type == "明槓":
            # 手札中に tile が3枚あり、捨て牌に1枚ある
            # → 実際は「手札3枚のみを tiles_to_remove に入れて、
            #    process_meld 内で target_tile 分の除去はself.discardsから自動」
            # → or まとめて4枚にして process_meld へ渡す
            #   (ただし process_meld で discardを再度除去するかなど、仕様次第)
            kan_tiles = [tile]*3
        elif kan_type == "加槓":
            # すでに pons に[tile, tile, tile] があり、手札に tile が1枚
            # → pons から取り除き、合計4枚分にする
            #   (ここで pon_setは [tile,tile,tile] のはず)
            kan_tiles = None
            for pon_set in self.players[player_id].pons:
                if len(pon_set) == 3 and pon_set[0].is_same_tile(tile):
                    kan_tiles = pon_set + [tile]
                    # ponsから pon_set を削除
                    self.players[player_id].pons.remove(pon_set)
                    # 手札1枚削除(= tile) → process_meld で除去してもOK
                    #   どちらでやるか仕様次第
                    break
            if not kan_tiles:
                print("[エラー] 加槓対象のポンが見つかりません")
                return
        else:
            print("[エラー] 不明なカンの種類:", kan_type)
            return

        # 3) 共通メルド処理を呼ぶ
        #    ただし "kan" の場合、 process_meld の仕組みに合わせて
        #    tiles_to_remove をどう渡すか決める
        if kan_type == "加槓":
            # pon_set + [tile] の合計4枚を process_meld に丸ごと渡す
            # → process_meld 内で for t in tiles_to_remove: remove_tile(t) → 4枚消える
            #   & ponsにはもうremoveしたので何もしない
            self.process_meld(player_id, "kan", kan_tiles, state)
        else:
            # 暗槓 or 明槓の場合は手牌にある3枚 or 4枚のみを process_meld に渡す形
            #  * 明槓の場合: tileが3枚
            #  * 暗槓の場合: tileが4枚
            self.process_meld(player_id, "kan", kan_tiles, state)

        # 4) 嶺上牌ツモ（ゲーム仕様次第）
        #    カン成立後に1枚ツモするなど
        new_tile = self.draw_tile(player_id)
        if new_tile:
            self.players[player_id].add_tile(new_tile)
            print(f"[カン後の嶺上牌をツモ] {new_tile}")
        else:
            print("[エラー] カン後に山が尽きました。ゲーム終了扱い？")
            # state.transition_to(GAME_END_PHASE) など、仕様に応じて

    # ==============
    # 追加実装例: prepare_kan_tiles
    # ==============
    def prepare_kan_tiles(self, player_id, tile, kan_type):
        """
        暗槓/明槓/加槓に応じて、手札から除去すべき牌リストを返す例。
          - tile: カンの基準となる牌
          - kan_type: '暗槓' or '明槓' or '加槓'
        """
        player = self.players[player_id]
        same_tiles = [t for t in player.tiles if t.is_same_tile(tile)]

        if kan_type == "暗槓":
            # 手札に同じ牌が4枚ないといけない
            if len(same_tiles) < 4:
                return []
            return same_tiles[:4]

        elif kan_type == "明槓":
            # (捨て牌1枚 + 手札3枚) → target_tile は tile と同じ？
            # ここでは "tile" が同じオブジェクトと仮定
            if len(same_tiles) < 3:
                return []
            return same_tiles[:3]

        elif kan_type == "加槓":
            # 既に pon している同じ tile が [tile, tile, tile] + 手札1枚
            # 1) ponセットを探す
            pon_set = None
            for pset in player.pons:
                # pset が [x, x, x] で x.is_same_tile(tile)
                if pset and pset[0].is_same_tile(tile):
                    pon_set = pset
                    break

            if not pon_set:
                print("[エラー] 加槓: pon済みの牌が見つかりません")
                return []

            # 2) 手札に1枚あればOK
            if len(same_tiles) < 1:
                print("[エラー] 加槓: 手札に追加1枚がありません")
                return []

            # 実際には "ponの3枚" をどう管理するかが課題
            # ここでは「pon_setには変更を加えず、単に手札1枚だけ除去して meldへ…」 という簡易実装
            return same_tiles[:1]

        else:
            print("[エラー] 不明なkan_type")
            return []
