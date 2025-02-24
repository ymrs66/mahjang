# File: core/meld_manager.py
from core.constants import *
from meld_checker import MeldChecker

class MeldManager:
    def __init__(self, game):
        """
        :param game: Gameインスタンス（players, discards, wallなどを参照するため）
        """
        self.game = game

        # meld_enabled や meld_candidates なども、
        # 必要であればこちらで持つことができる (あるいは Game 側に置いたままでもOK)
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

    def check_all_melds(self, player_id, discard_tile):
        """
        ポン/チー/カンをまとめて判定し、結果を自分のメンバに保持。
        あるいは結果を返すことも可能。
        """
        player = self.game.players[player_id]
        tiles = player.tiles
        pons  = player.pons

        result = MeldChecker.check_all_melds(tiles, pons, discard_tile)

        self.meld_candidates["pon"] = result["pon_candidates"]
        self.meld_candidates["chi"] = result["chi_candidates"]
        self.meld_candidates["kan"] = result["kan_candidates"]

        self.meld_enabled["pon"] = (len(result["pon_candidates"]) > 0)
        self.meld_enabled["chi"] = (len(result["chi_candidates"]) > 0)
        self.meld_enabled["kan"] = (len(result["kan_candidates"]) > 0)

        if discard_tile is not None:
            self.target_tile = discard_tile

        return result

    def clear_meld_state(self):
        """
        メルドに関する状態をリセットしたいときに呼ぶ (target_tile, meld_candidates, etc.)
        """
        self.target_tile = None
        for k in self.meld_candidates:
            self.meld_candidates[k] = []
        for k in self.meld_enabled:
            self.meld_enabled[k] = False

    def process_meld(self, player_id, meld_type, tiles_to_remove, state):
        """
        汎用的なメルド実行処理
        (Gameにあった process_meld のロジックを移行)
        """
        player = self.game.players[player_id]

        # 1) 手札から除去
        for t in tiles_to_remove:
            print(f"  [process_meld] remove_tile({t}) を実行します。手牌: {player.tiles}")
            player.remove_tile(t)
            print(f"  [process_meld] remove_tile後の手牌: {player.tiles}")

        # 2) 捨て牌から1枚除去 (self.target_tile がある場合)
        if self.target_tile:
            self.game.discards[1] = [
                d for d in self.game.discards[1]
                if not d.is_same_tile(self.target_tile)
            ]

        # 3) メルド先に追加
        if meld_type == "pon":
            player.pons.append(tiles_to_remove + [self.target_tile])
        elif meld_type == "chi":
            player.chis.append(tiles_to_remove + [self.target_tile])
        elif meld_type == "kan":
            player.kans.append(tiles_to_remove + [self.target_tile])
        else:
            print(f"[警告] 不明なmeld_type: {meld_type}")

        print(f"{meld_type}成功: {tiles_to_remove + [self.target_tile]}")
        self.meld_enabled[meld_type] = False
        self.target_tile = None

        # 4) フェーズ遷移
        state.waiting_for_player_discard = False
        state.transition_to(PLAYER_DISCARD_PHASE)

    def process_pon(self, player_id, state):
        """
        (Game.process_pon) を移行。
        """
        if not self.meld_enabled["pon"] or self.target_tile is None:
            return

        pon_sets = self.meld_candidates["pon"]
        if not pon_sets:
            print("[エラー] pon候補がありません")
            return

        pon_set = pon_sets[0]
        tiles_to_remove = pon_set[:-1]
        self.process_meld(player_id, "pon", tiles_to_remove, state)

    def process_chi(self, player_id, chosen_sequence, state):
        """
        (Game.process_chi) を移行。
        """
        if not self.meld_enabled["chi"] or self.target_tile is None:
            return

        seq_without_discard = [t for t in chosen_sequence if not t.is_same_tile(self.target_tile)]
        self.process_meld(player_id, "chi", seq_without_discard, state)

    def process_kan(self, player_id, tile, state):
        """
        (Game.process_kan) を移行。
        """
        if not self.meld_enabled["kan"]:
            print("[エラー] カンが有効でない状態です")
            return

        # ここで暗槓/明槓/加槓を判定 → 除去すべき牌を確定
        kan_type = self.determine_kan_type(player_id, tile)
        if kan_type is None:
            print("[エラー] カンできない or 不明な種類")
            return

        # ... (暗槓/明槓/加槓 の除去ロジック)
        # → self.process_meld( ... ) を呼ぶ

        # カン完了後、嶺上牌ツモするなど…

    def determine_kan_type(self, player_id, tile):
        """
        ここで暗槓/明槓/加槓を判定 (Game.determine_kan_type) を移行。
        """
        # ここでは self.game.discards や self.target_tile を参照
        # ...
        pass

    # 必要に応じて prepare_kan_tiles(...) などのヘルパーもこちらに置く