# File: mahjang/phases/win_result_phase.py
import pygame
from phases.base_phase import BasePhase
from core.constants import PLAYER_DRAW_PHASE, GAME_END_PHASE, AI_ACTION_DELAY
from core.resource_utils import get_resource_path

class WinResultPhase(BasePhase):
    def __init__(self, game, state):
        super().__init__(game, state)
        # 結果表示開始時刻
        self.start_time = pygame.time.get_ticks()
        # 表示期間（ミリ秒）
        self.display_duration = 5000  # 例：5000ms = 5秒

        # 既に process_ron/tsumo で設定済みのプロパティがなければ初期値を設定
        if not hasattr(self.state, 'win_message'):
            self.state.win_message = "和了！"
        if not hasattr(self.state, 'win_yaku'):
            self.state.win_yaku = []
        if not hasattr(self.state, 'win_score'):
            self.state.win_score = 0

    def update(self, current_time):
        # 一定時間表示後、またはイベント（キー入力など）で早期終了できるようにする
        if current_time - self.start_time > self.display_duration:
            print("[WinResultPhase] 結果表示終了 → 次のフェーズへ")
            # ここでプレイヤーの手牌を再セット or 削除
            self.state.game.players[0].tiles.clear()
            self.state.game.players[1].tiles.clear()

            # ここでは例として PLAYER_DRAW_PHASE に遷移（局のリスタートなど）
            self.state.transition_to(PLAYER_DRAW_PHASE)

    def handle_event(self, event):
        # キー入力で早期終了させる例
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("[WinResultPhase] スペースキーで結果表示終了")
                self.state.transition_to(PLAYER_DRAW_PHASE)

    def render(self, screen):
        """
        WinResultPhaseの描画: 勝利メッセージや和了手牌などを描画する
        """
        # 背景は前段 (ui_manager.render) で塗りつぶされている想定でもOK。
        # ここで改めて塗るならこんな感じ:
        screen.fill((0, 0, 0))  # 真っ黒にする例

        # フォントで文字を描く例
        font_path = get_resource_path("fonts/meiryo.ttc")
        large_font = pygame.font.Font(font_path, 48) if font_path else pygame.font.SysFont("Arial", 48)
        small_font = pygame.font.Font(font_path, 24) if font_path else pygame.font.SysFont("Arial", 24)

        # メッセージ表示
        win_text = self.state.win_message
        win_surface = large_font.render(win_text, True, (255, 255, 0))
        win_rect = win_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(win_surface, win_rect)

        # プレイヤーの最終手牌を軽く表示
        hand_x = 50
        hand_y = SCREEN_HEIGHT - 80
        for tile in self.state.game.players[0].tiles:
            if tile.image:
                screen.blit(tile.image, (hand_x, hand_y))
            hand_x += TILE_WIDTH + TILE_MARGIN

        # 役のリストなど
        y_offset = 200
        for role in self.state.win_yaku:
            role_surface = small_font.render(role, True, (255, 255, 255))
            screen.blit(role_surface, (50, y_offset))
            y_offset += 30

        score_surface = small_font.render(f"Score: {self.state.win_score}", True, (255, 255, 255))
        screen.blit(score_surface, (50, y_offset + 20))
