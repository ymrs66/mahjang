##main.py
import pygame
from core.game import Game
from core.game_state import GameState
from phases.riichi_phase import PlayerRiichiPhase
from core.constants import (
    PLAYER_DISCARD_PHASE,
    PLAYER_DRAW_PHASE,
    AI_DRAW_PHASE,
    AI_DISCARD_PHASE,
    MELD_WAIT_PHASE,
    AI_ACTION_SELECTION_PHASE,
    PLAYER_ACTION_SELECTION_PHASE,
    PLAYER_RIICHI_PHASE,
    GAME_END_PHASE
)
from events.event_handler import handle_events  # イベント処理を外部モジュールに分離
from core.game_logic import (
    handle_ai_action_selection_phase,
    handle_player_action_selection_phase,
    handle_meld_wait_phase
)
# 描画関連
from drawing.player_drawing import draw_player_state # プレイヤーの手牌・ポン・チーを描画
from drawing.ai_drawing import draw_ai_tiles
from drawing.discard_drawing import draw_discards
from drawing.ui_drawing import draw_action_buttons
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from phases.draw_phase import PlayerDrawPhase, AIDrawPhase
from phases.discard_phase import PlayerDiscardPhase, AIDiscardPhase

# Pygame初期設定
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("麻雀ゲーム")
clock = pygame.time.Clock()

# メインループ
def main_loop():
    """
    ゲームのメインループ
    """
    game = Game()
    game.shuffle_wall()
    game.deal_initial_hand()

    state = GameState()
    state.initialize(game)

    # ① フェーズID→処理関数 のマッピングを用意
    phase_handlers = {
        AI_DRAW_PHASE:   lambda st, ct: AIDrawPhase(st.game, st).update(ct),
        AI_DISCARD_PHASE: lambda st, ct: AIDiscardPhase(st.game, st).update(ct),
        PLAYER_DRAW_PHASE: lambda st, ct: PlayerDrawPhase(st.game, st).update(ct),
        PLAYER_RIICHI_PHASE:   lambda st, ct: PlayerRiichiPhase(st.game, st).update(ct),
        PLAYER_DISCARD_PHASE: lambda st, ct: PlayerDiscardPhase(st.game, st).update(ct),
        AI_ACTION_SELECTION_PHASE: handle_ai_action_selection_phase,
        PLAYER_ACTION_SELECTION_PHASE: handle_player_action_selection_phase,
        MELD_WAIT_PHASE: handle_meld_wait_phase,
    }

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # 1. イベント処理
        if not handle_events(state, current_time, screen):
            running = False
            break

        # 2. フェーズに応じた処理を呼ぶ
        if state.current_phase == GAME_END_PHASE:
            print("[ゲーム終了] ゲームが終了しました")
            running = False
        else:
            # ② マッピングで関数を取り出して呼ぶ
            handler = phase_handlers.get(state.current_phase)
            if handler:
                handler(state, current_time)
            else:
                # 未定義フェーズなら警告して終了
                print(f"[警告] 未知のフェーズ: {state.current_phase}")
                running = False

        # 3. 描画処理
        render_game(state)

        # 4. フレームレート制御
        clock.tick(30)

    pygame.quit()

# 描画処理
def render_game(state):
    """
    画面描画を管理する
    """
    screen.fill((0, 128, 0))  # 背景色
    draw_player_state(screen, state.game.players[0], state.selected_tile)  # プレイヤーの手牌・ポン・チーを描画
    draw_ai_tiles(screen)
    draw_discards(screen, state.game.discards)

    if (state.current_phase in [PLAYER_ACTION_SELECTION_PHASE, PLAYER_RIICHI_PHASE]) \
    and state.available_actions:
        # 毎フレーム、行動ボタンを描画して Rect を更新
        state.action_buttons = draw_action_buttons(screen, state.available_actions)    
    pygame.display.flip()
    
if __name__ == "__main__":
    main_loop()