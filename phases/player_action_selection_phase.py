# phases/player_action_selection_phase.py
from .base_phase import BasePhase
from core.constants import (
    GAME_END_PHASE,
    PLAYER_DRAW_PHASE,
    AI_DRAW_PHASE,
    PLAYER_ACTION_SELECTION_PHASE,
    AI_ACTION_DELAY
)

class PlayerActionSelectionPhase(BasePhase):
    """
    もともと game_logic.py の handle_player_action_selection_phase(state, current_time)
    の内容をこちらへ移植。
    """

    def update(self, current_time):
        """
        フェーズが毎フレーム呼び出されるときの処理。
        もとの handle_player_action_selection_phase(state, current_time) のロジックを移行。
        """
        print("[PlayerActionSelectionPhase] update")

        # 1) もし「ツモ」が可能ならポンチー等はスキップ
        if "ツモ" in self.state.available_actions:
            print("[PlayerActionSelectionPhase] 既にツモ可能 → 副露判定はスキップ")
            return

        # 2) AIの捨て牌がなければスキップ → 次のフェーズ
        if not self.state.game.discards[1]:
            print("[PlayerActionSelectionPhase] AIの捨て牌がないためスキップ → PLAYER_DRAW_PHASEへ")
            self.state.transition_to(PLAYER_DRAW_PHASE)
            return

        # 3) 捨て牌(最後の1枚)を取り出し、プレイヤーが可能なアクションを取得
        discard_tile = self.state.game.discards[1][-1]
        actions = self.state.game.get_available_actions(player_id=0, discard_tile=discard_tile)

        if actions:
            print(f"[PlayerActionSelectionPhase] 選択可能アクション: {actions}")
            self.state.available_actions = actions
        else:
            print("[PlayerActionSelectionPhase] アクションなし → AIのターン(AI_DRAW_PHASE)")
            self.state.ai_action_time = current_time + AI_ACTION_DELAY
            self.state.transition_to(AI_DRAW_PHASE)

    def handle_event(self, event):
        """
        イベント処理 (マウスクリックやキー入力など)。
        ボタンをクリックして「ポン/チー/カン/ツモ/スキップ」などを実行する。
        
        本来は event_handler.py で似た処理をしていますが、
        それをフェーズクラス内に取り込む方法の例です。
        """
        import pygame
        from core.constants import AI_ACTION_DELAY, PLAYER_DRAW_PHASE
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # state.action_buttons に {"ポン": rect, "チー": rect, ...} があると想定
            for action, rect in self.state.action_buttons.items():
                if rect.collidepoint(pos):
                    print(f"[PlayerActionSelectionPhase] ボタン '{action}' がクリックされました")

                    if action == "ポン":
                        self.do_pon()
                    elif action == "チー":
                        self.do_chi()
                    elif action == "カン":
                        self.do_kan()
                    elif action == "ツモ":
                        self.do_tsumo()
                    elif action == "ロン":
                        self.do_ron()
                    elif action == "スキップ":
                        # スキップ → AIツモへ
                        self.state.ai_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY
                        self.state.transition_to(AI_DRAW_PHASE)
                    # 処理後は break でも可
                    return

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # ツモが候補にある場合はスキップできない → など制御
            if "ツモ" in self.state.available_actions:
                print("[Info] ツモ可能なのでスペースではスキップ不可")
            else:
                print("[Info] スペース → スキップ")
                self.state.transition_to(PLAYER_DRAW_PHASE)

    # --- 以下、具体的な副露アクション ---
    def do_pon(self):
        if self.state.game.meld_manager.meld_enabled["pon"]:
            self.state.game.meld_manager.process_pon(0, self.state)
        else:
            print("[Error] ポンできる状態ではありません")

    def do_chi(self):
        if self.state.game.meld_manager.meld_enabled["chi"]:
            chi_list = self.state.game.meld_manager.meld_candidates["chi"]
            if chi_list:
                chosen_sequence = chi_list[0]
                self.state.game.meld_manager.process_chi(0, chosen_sequence, self.state)
            else:
                print("[Error] チー候補が存在しない")
        else:
            print("[Error] チーできる状態ではありません")

    def do_kan(self):
        if self.state.game.meld_manager.meld_enabled["kan"]:
            kan_list = self.state.game.meld_manager.meld_candidates["kan"]
            if kan_list:
                kan_tile = kan_list[0]
                self.state.game.meld_manager.process_kan(0, kan_tile, self.state)
            else:
                print("[Error] カン候補が存在しない")
        else:
            print("[Error] カンできる状態ではありません")

    def do_tsumo(self):
        print("[Action] ツモ実行")
        self.state.game.process_tsumo(0, self.state)

    def do_ron(self):
        # （例）AIが捨てた最後の牌を取得
        #   もし捨てたのがプレイヤー1だけとは限らない場合は、対象プレイヤーIDをその都度決める必要あり。
        #   とりあえず2人対戦で「他家＝AI＝1番」と想定:
        if self.state.game.discards[1]:
            discard_tile = self.state.game.discards[1][-1]
        else:
            discard_tile = None

        print(f"[DEBUG] do_ron() called. discard_tile={discard_tile}")

        if discard_tile:
            self.state.game.process_ron(0, discard_tile, self.state)
        else:
            print("[Error] ロン対象の捨て牌がありません")
