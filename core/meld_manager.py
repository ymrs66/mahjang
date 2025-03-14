# File: core/meld_manager.py
import pygame
from core.constants import *
from meld_checker import MeldChecker

class MeldManager:
    def __init__(self, game):
        """
        :param game: Gameインスタンス（players, discards, wallなどを参照するため）
        """
        self.game = game

        # 「ポン/チー/カン」それぞれの成立可否と候補セット
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

    def check_all_melds(self, player_id, discard_tile):
        """
        ポン/チー/カンをまとめて判定し、結果を self.meld_candidates と self.meld_enabled に保持。
        discard_tile は「他家が捨てた牌」を外部から渡す。
        """
        player = self.game.players[player_id]
        tiles = player.tiles
        pons  = player.pons

        # meld_checker.py のロジックを呼び出す
        result = MeldChecker.check_all_melds(tiles, pons, discard_tile)

        self.meld_candidates["pon"] = result["pon_candidates"]
        self.meld_candidates["chi"] = result["chi_candidates"]
        self.meld_candidates["kan"] = result["kan_candidates"]

        self.meld_enabled["pon"] = (len(result["pon_candidates"]) > 0)
        self.meld_enabled["chi"] = (len(result["chi_candidates"]) > 0)
        self.meld_enabled["kan"] = (len(result["kan_candidates"]) > 0)

        return result

    def clear_meld_state(self):
        """
        メルドに関する状態をリセットしたいときに呼ぶ。
        """
        for k in self.meld_candidates:
            self.meld_candidates[k] = []
        for k in self.meld_enabled:
            self.meld_enabled[k] = False


    def process_meld(self, player_id, meld_type, discard_tile, tiles_to_remove, state):
        """
        汎用的なメルド実行処理。discard_tile(捨て牌)も引数で受け取り、必要に応じて捨て牌リストから除去する。

        :param player_id: メルドを行うプレイヤーID
        :param meld_type: "pon"/"chi"/"kan" のいずれか
        :param discard_tile: 他家が捨てた牌 (Tile)
        :param tiles_to_remove: 手牌から除去する牌リスト（刻子/順子など）
        :param state: GameState オブジェクト
        """
        player = self.game.players[player_id]

        # --- 1) 手札から除去 ---
        for t in tiles_to_remove:
            print(f"  [process_meld] remove_tile({t}) を実行します。手牌: {player.tiles}")
            player.remove_tile(t)
            print(f"  [process_meld] remove_tile後の手牌: {player.tiles}")

        # --- 2) 捨て牌から除去 (discard_tileがあれば1枚だけ消す) ---
        if discard_tile:
            # 例として「AIの捨て牌一覧(discards[1]) から除く」等
            # あなたの仕様にあわせて調整してください。通常は「他家の捨て牌」を消します。
            self.game.discards[1] = [
                d for d in self.game.discards[1]
                if not d.is_same_tile(discard_tile)
            ]

        # --- 3) メルド先に追加 ---
        if meld_type == "pon":
            player.is_menzen = False
            player.pons.append(tiles_to_remove + [discard_tile])
        elif meld_type == "chi":
            player.is_menzen = False
            player.chis.append(tiles_to_remove + [discard_tile])
        elif meld_type == "kan":
            kan_type = self.game.determine_kan_type(player_id, discard_tile)
            if kan_type in ("明槓", "加槓"):
                player.is_menzen = False
            player.kans.append(tiles_to_remove + [discard_tile])
        else:
            print(f"[警告] 不明なmeld_type: {meld_type}")

        print(f"{meld_type}成功: {tiles_to_remove + [discard_tile]}")
        self.meld_enabled[meld_type] = False

        # --- 4) フェーズ遷移 ---
        state.ai_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY
        state.waiting_for_player_discard = False
        state.transition_to(PLAYER_DISCARD_PHASE)


    def process_pon(self, player_id, discard_tile, state):
        """
        ポン処理:
          - discard_tile(捨て牌) を外部から受け取り
          - pon_candidates から最初の候補を取り出して process_meld() を呼ぶ
        """
        if not self.meld_enabled["pon"]:
            print("[エラー] ポンが有効になっていません")
            return

        pon_sets = self.meld_candidates["pon"]
        if not pon_sets:
            print("[エラー] pon候補がありません")
            return

        # pon_sets[0] は [A, B, discard_tile] という3枚セット想定
        pon_set = pon_sets[0]
        tiles_to_remove = pon_set[:-1]  # 手札から除去する2枚
        self.process_meld(player_id, "pon", discard_tile, tiles_to_remove, state)

    def process_chi(self, player_id, discard_tile, chosen_sequence, state):
        """
        チー処理:
          - discard_tile と chosen_sequence( [Tile, Tile, discard_tile] ) を受け取る
          - discard_tile以外を手札から除去してメルド。
        """
        if not self.meld_enabled["chi"]:
            print("[エラー] チーが有効になっていません")
            return

        seq_without_discard = [t for t in chosen_sequence if not t.is_same_tile(discard_tile)]
        self.process_meld(player_id, "chi", discard_tile, seq_without_discard, state)

    def process_kan(self, player_id, discard_tile, tile, state):
        """
        カン処理:
          - discard_tile(捨て牌) or None
          - tile: カン対象の牌（明槓/加槓なら discard_tile と同一 or 既存のポン牌）
        """
        if not self.meld_enabled["kan"]:
            print("[エラー] カンが有効になっていません")
            return

        kan_type = self.game.determine_kan_type(player_id, tile)
        if kan_type is None:
            print("[エラー] カンできない or 不明な種類")
            return

        # ここで prepare_kan_tiles(...) 相当のロジックを呼び出し
        # 例: 
        tiles_to_remove = self.game.prepare_kan_tiles(player_id, tile, kan_type)
        if not tiles_to_remove:
            print("[エラー] カン用の牌が不足しています")
            return

        # カンメルドを実行
        self.process_meld(player_id, "kan", discard_tile, tiles_to_remove, state)
        # カン後の「嶺上牌ツモ」などはここで行う（必要に応じて実装）


    def determine_kan_type(self, player_id, tile):
        """
        Gameクラスの determine_kan_type をそのまま呼んでもいいし、
        又はこのメソッド内に同じロジックを移植してもOK。
        """
        return self.game.determine_kan_type(player_id, tile)
