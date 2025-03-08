# phases/base_phase.py
import pygame
class BasePhase:
    def __init__(self, game, state):
        self.game = game
        self.state = state

    def handle_event(self, event):
        # 共通のイベント処理例
        if event.type == pygame.KEYDOWN:
            # 例えば F1 キーでヘルプ表示（必要なら実装を拡張）
            if event.key == pygame.K_F1:
                print("[BasePhase] ヘルプを表示します")
            elif event.key == pygame.K_ESCAPE:
                print("[BasePhase] ESCキーが押されました → ゲーム終了要求")
                # GameState に終了フラグをセットする例（未実装の場合はコメントアウト）
                # self.state.end_game()
        # 他の共通処理があればここに追加
    def update(self, current_time):
        """フェーズの更新処理"""
        pass

    def render(self, screen):
        """描画処理"""
        pass