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
    PLAYER_RIICHI_PHASE,
    PLAYER_SELECT_TILE_PHASE,
    GAME_END_PHASE
)
from core.resource_utils import get_resource_path
from core.constants import DEFAULT_FONT_PATH
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
    """ゲームの状態に応じた描画をまとめて行う"""
    # 背景描画
    draw_background(screen)

    # プレイヤーの手牌描画（選択中の牌をハイライト）
    draw_player_state(screen, state.game.players[0], state.selected_tile,state.drawn_tile)
    # AIの手牌描画
    draw_ai_tiles(screen)
    # 捨て牌描画
    draw_discards(screen, state.game.discards)

    # UIボタンの描画（必要な場合のみ）
    if state.current_phase in [PLAYER_DISCARD_PHASE,
                               PLAYER_ACTION_SELECTION_PHASE,
                               PLAYER_RIICHI_PHASE,
                               PLAYER_SELECT_TILE_PHASE] and state.available_actions:
        state.action_buttons = draw_action_buttons(screen, state.available_actions)

    pygame.display.flip()