# File: mahjang/drawing/renderer.py
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.constants import (
    PLAYER_DISCARD_PHASE,
    PLAYER_DRAW_PHASE,
    AI_DRAW_PHASE,
    AI_DISCARD_PHASE,
    MELD_WAIT_PHASE,
    AI_ACTION_SELECTION_PHASE,
    PLAYER_ACTION_SELECTION_PHASE,
    PLAYER_SELECT_TILE_PHASE,
    WIN_RESULT_PHASE,
    GAME_END_PHASE
)
from core.resource_utils import get_resource_path
from core.constants import DEFAULT_FONT_PATH,TILE_WIDTH,TILE_MARGIN,SCREEN_HEIGHT,SCREEN_WIDTH 
from drawing.player_drawing import draw_player_state
from drawing.ai_drawing import draw_ai_tiles
from drawing.discard_drawing import draw_discards
from drawing.ui_drawing import draw_action_buttons

def draw_background(screen):
    """画面全体の背景を描画する"""
    # 背景色を緑に設定（例）
    screen.fill((0, 128, 0))

def draw_button(screen, rect, text, bg_color, text_color=(0, 0, 0), font_size=24):
    """
    指定された矩形にボタンを描画する共通関数
    :param screen: 描画先のPygameスクリーン
    :param rect: pygame.Rectオブジェクト
    :param text: ボタンに表示するテキスト
    :param bg_color: ボタンの背景色
    :param text_color: テキスト色（デフォルト：黒）
    :param font_size: フォントサイズ（デフォルト：24）
    :return: 描画したボタンのRect
    """
    pygame.draw.rect(screen, bg_color, rect)
    font_path = get_resource_path(DEFAULT_FONT_PATH)
    if font_path:
        font = pygame.font.Font(font_path, font_size)
        rendered_text = font.render(text, True, text_color)
        # テキストを中央に配置
        text_rect = rendered_text.get_rect(center=rect.center)
        screen.blit(rendered_text, text_rect)
    return rect

def render_game_state(state, screen):
    """
    ゲームの状態に応じた描画をまとめて行う。
    WinResultPhase(WIN_RESULT_PHASE) かどうかで分岐し、
    通常フェーズは共通描画を行う。
    """
    # 1) 特殊フェーズ(例: 勝利結果)の判定
    if state.current_phase == WIN_RESULT_PHASE:
        render_win_result_phase(state, screen)
        pygame.display.flip()
        return

    # 2) 通常フェーズの卓面描画
    draw_background(screen)

    # プレイヤー手牌
    draw_player_state(
        screen=screen,
        player=state.game.players[0],
        selected_tile=state.selected_tile,
        drawn_tile=state.drawn_tile
    )
    # AI手牌(裏面)
    draw_ai_tiles(screen)

    # 捨て牌
    draw_discards(screen, state.game.discards)

    # 必要があればアクションボタンなど
    if state.current_phase in [
        PLAYER_DISCARD_PHASE,
        PLAYER_ACTION_SELECTION_PHASE,
        PLAYER_SELECT_TILE_PHASE,
    ] and state.available_actions:
        # ボタン描画用の関数(例: draw_action_buttons)
        state.action_buttons = draw_action_buttons(screen, state.available_actions)

    pygame.display.flip()


def render_win_result_phase(state, screen):
    """
    WinResultPhase用の描画: 黒背景 + 勝利テキストや手牌表示等
    """
    # 画面を真っ黒に塗りつぶし
    screen.fill((0, 0, 0))

    # 大きめのフォントで勝利メッセージを表示
    font_path = get_resource_path(DEFAULT_FONT_PATH)
    large_font = pygame.font.Font(font_path, 48) if font_path else pygame.font.SysFont("Arial", 48)
    small_font = pygame.font.Font(font_path, 24) if font_path else pygame.font.SysFont("Arial", 24)

    # Winメッセージ
    win_text = state.win_message  # 例: "ロン和了！" / "ツモ和了！" 等
    text_surface = large_font.render(win_text, True, (255, 255, 0))
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(text_surface, text_rect)

    # プレイヤーの最終手牌表示（サムネイル）
    hand_x = 50
    hand_y = SCREEN_HEIGHT - 80
    for tile in state.game.players[0].tiles:
        if tile.image:
            screen.blit(tile.image, (hand_x, hand_y))
        hand_x += TILE_WIDTH + TILE_MARGIN

    # 役のリストや点数表示
    y_offset = 200
    for role in state.win_yaku:  # 例: ["タンヤオ", "ピンフ"] 等
        role_surface = small_font.render(role, True, (255, 255, 255))
        screen.blit(role_surface, (50, y_offset))
        y_offset += 30

    score_surface = small_font.render(f"Score: {state.win_score}", True, (255, 255, 255))
    screen.blit(score_surface, (50, y_offset + 20))