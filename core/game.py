# File: mahjang\core\game.py

import random
from core.tile import Tile
from core.hand import Hand
from ai.ai_player import AIPlayer
from core.player import Player
from core.constants import *
# meld_checker.py をインポート
from meld_checker import is_win_hand
from core.meld_manager import MeldManager
from core.yaku_caliculator import calculate_yaku

class Game:
    def __init__(self):
        self.tile_cache = {}
        self.wall = self.generate_wall()
        self.players = [Player(), AIPlayer(1)]
        self.discards = [[], []]
        self.meld_manager = MeldManager(self)  # ここでコンストラクタに self を渡す
        self.target_tile = None


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
        """
        従来はここで MeldChecker を呼んでいたが、MeldManagerに移行。
        """
        return self.meld_manager.check_all_melds(player_id, discard_tile)


    def get_available_actions(self, player_id, discard_tile):
        """
        ポン/チー/カン判定をまとめて呼び出し、
        実行可能なアクション名をリストで返す。
        """
        player = self.players[player_id]

        # --- 1) リーチ中ならポン・チー・カンを無効化する ---
        #     ここで「リーチした player_id 自身が鳴けない」ようにする。
        #     もし「他家が鳴けない」ルールなら、別の判定が必要。
        if player.is_reach:
            # リーチ中のプレイヤーは鳴き不可
            pon_enabled = False
            chi_enabled = False
            kan_enabled = False
        else:
            # --- 通常通りメルドチェック ---
            self.meld_manager.check_all_melds(player_id, discard_tile)
            pon_enabled = self.meld_manager.meld_enabled["pon"]
            chi_enabled = self.meld_manager.meld_enabled["chi"]
            kan_enabled = self.meld_manager.meld_enabled["kan"]

        actions = []
        if pon_enabled:
            actions.append("ポン")
        if chi_enabled:
            actions.append("チー")
        if kan_enabled:
            actions.append("カン")

        # 2) ロン判定
        temp_tiles = player.tiles.copy()
        temp_tiles.append(discard_tile)   # 14枚になる
        if is_win_hand(temp_tiles):
            actions.append("ロン")

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

            # --- メルドリセットは MelsManagerにまとめる ---
            self.meld_manager.clear_meld_state()

            #self.target_tile = None

        else:
            discarded_tile = self.players[1].discard_tile()
            if discarded_tile:
                self.discards[1].append(discarded_tile)
                print(f"AIが捨てた牌: {discarded_tile}")
                self.target_tile = discarded_tile
                print(f"[DEBUG] game.target_tile after AI discard: {self.target_tile}")
            else:
                print("エラー: AIが捨て牌を選択できませんでした！")

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

    def process_ron(self, player_id, discard_tile, state):
        print(f"[ロン宣言] プレイヤー{player_id}が {discard_tile} をロンしました！")
        # 対象の捨て牌を削除（既存の処理）
        if player_id == 0:
            if discard_tile in self.discards[1]:
                self.discards[1].remove(discard_tile)
        else:
            if discard_tile in self.discards[0]:
                self.discards[0].remove(discard_tile)
    
        winning_tiles = self.players[player_id].tiles.copy()
        winning_tiles.append(discard_tile)
        print(f"[ロン] {winning_tiles} で和了！")
    
        # プレイヤーの手牌に加える
        self.players[player_id].tiles.append(discard_tile)
    
        # 役計算実施（ロンの場合、concealed_hand は通常は鳴いていないので簡単化）
        concealed_hand = self.players[player_id].tiles  
        melds = self.players[player_id].pons + self.players[player_id].chis + self.players[player_id].kans
        player=state.game.players[0]
        yaku_list, han = calculate_yaku(concealed_hand, melds, discard_tile, False, player)
    
    
        state.win_message = "ロン和了！"
        state.win_yaku = yaku_list
        state.win_score = han * 1000  # 仮の点数例
    
        state.transition_to(WIN_RESULT_PHASE)
        
    def process_tsumo(self, player_id, state):
        winning_tiles = state.game.players[player_id].tiles.copy()  # 14枚
        print(f"[ツモ宣言] プレイヤー{player_id}が自摸和了しました！")
        print(f"[ツモ] {winning_tiles} で和了！")
    
        # ここで役計算を実行（現時点では calculate_yaku を使った例）
        # 例えば、隠し手牌は player.tiles の中から鳴き牌を除いたもの（簡略化のため全体で計算）
        concealed_hand = state.game.players[player_id].tiles  
        melds = state.game.players[player_id].pons + state.game.players[player_id].chis + state.game.players[player_id].kans
        player=state.game.players[0]
        yaku_list, han = calculate_yaku(concealed_hand, melds, None, True, player)
    
        # GameState に結果をセット
        state.win_message = "ツモ和了！"
        state.win_yaku = yaku_list
        state.win_score = han * 1000  # 仮の点数計算例（1翻＝1000点とする）
    
        # WinResultPhase へ遷移
        state.transition_to(WIN_RESULT_PHASE)

    
    def process_ai_tsumo(self,player_id, state):
        winning_tiles = self.players[player_id].tiles.copy()
        print(f"[AIツモ宣言] プレイヤー{player_id}がツモ和了しました！")
        print(f"[ツモ] {winning_tiles}")
        # ここで点数計算 etc...
        state.transition_to(GAME_END_PHASE)
    
    def process_kan(self, player_id, tile, state, kan_type):
        """
        カン処理を実行するメソッド
        :param player_id: カンを行うプレイヤーID
        :param tile: カン対象の牌
        :param state: ゲーム状態
        :param kan_type: "暗槓"、"明槓"、"加槓" のいずれか（文字列）
        """
        print(f"[カン処理] プレイヤー{player_id}が {kan_type} を実行します: {tile}")
        # ここで、例えば、必要な牌を手牌から除去して meld_manager で処理するなどの実装を行う
        # 例：
        tiles_to_remove = self.prepare_kan_tiles(player_id, tile, kan_type)
        if not tiles_to_remove:
            print("[エラー] カン用の牌が不足しています")
            return
        # meld_manager の process_meld を呼び出す例（実装に合わせて調整してください）
        self.meld_manager.process_meld(player_id, "kan", tiles_to_remove, state)
        # カン後の処理（例えば嶺上牌ツモなど）も必要ならここで実装