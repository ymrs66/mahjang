from game import Game
from drawing import draw_tiles, draw_ai_tiles, draw_discards
from events import handle_player_input
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, AI_ACTION_DELAY

# Pygame初期設定
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("麻雀ゲーム")
clock = pygame.time.Clock()

# ゲーム初期化
game = Game()
game.shuffle_wall()
game.deal_initial_hand()
tsumo_tile = game.draw_tile(0)  # プレイヤーが最初にツモ
selected_tile = None
ai_action_time = 0

# メインループ
def main_loop():
    global tsumo_tile, selected_tile, ai_action_time
    running = True

    while running:
        current_time = pygame.time.get_ticks()

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game.current_turn == 0:  # プレイヤーのターン
                tsumo_tile, selected_tile = handle_player_input(event, game, tsumo_tile, selected_tile, current_time)
                if game.current_turn == 1:  # プレイヤーの処理が終わり、AIのターンに移行
                    ai_action_time = current_time + AI_ACTION_DELAY  # 1秒後にAIが動作
        # AIの処理
        if game.current_turn == 1 and current_time >= ai_action_time:
            discard_tile = game.players[1].discard_tile()  # AIの打牌
            game.discards[1].append(discard_tile)
            game.current_turn = 2  # プレイヤーのツモを待機
            ai_action_time = current_time + AI_ACTION_DELAY

        # プレイヤーのツモ処理
        if game.current_turn == 2 and current_time >= ai_action_time:
            tsumo_tile = game.draw_tile(0)
            game.current_turn = 0

        # 描画
        draw_tiles(screen, game.players[0], tsumo_tile, selected_tile)
        draw_ai_tiles(screen)
        draw_discards(screen, game.discards)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main_loop()