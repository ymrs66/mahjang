from game import Game
from drawing import draw_tiles, draw_ai_tiles, draw_discards, draw_pon_button
from events import handle_player_input, handle_pon_click
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

            # プレイヤーのターン
            if game.current_turn == 0:
                tsumo_tile, selected_tile = handle_player_input(event, game, tsumo_tile, selected_tile, current_time)
                if game.current_turn == 1:
                    ai_action_time = current_time + AI_ACTION_DELAY

            # ポン待機状態の処理
            if game.current_turn == 3:
                if game.can_pon:
                    pon_button_rect = draw_pon_button(screen, True)
                    if handle_pon_click(event, pon_button_rect, game):  # ポンボタンがクリックされた場合
                        print("ポンしました")
                        game.current_turn = 0  # 捨て牌フェーズに移行
                        game.can_pon = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # スペースキーでスキップ
                        print("ポンをスキップしました")
                        game.current_turn = 2
                        game.can_pon = False

        # AIのターン
        if game.current_turn == 1 and current_time >= ai_action_time:
            discard_tile = game.players[1].discard_tile()
            if discard_tile is not None:
                game.discards[1].append(discard_tile)
                if game.check_pon(0, discard_tile):  # ポンのチェック
                    print(f"ポン可能: {discard_tile}")
                    game.current_turn = 3  # ポン待機状態
                else:
                    game.current_turn = 2  # ツモフェーズに移行
            else:
                game.current_turn = 2

            ai_action_time = current_time + AI_ACTION_DELAY

        # プレイヤーのツモ処理
        if game.current_turn == 2 and current_time >= ai_action_time:
            tsumo_tile = game.draw_tile(0)
            game.current_turn = 0

        # 描画
        screen.fill((0, 128, 0))  # 背景色
        draw_tiles(screen, game.players[0], tsumo_tile, selected_tile)
        draw_ai_tiles(screen)
        draw_discards(screen, game.discards)
        if game.can_pon:
            draw_pon_button(screen, True)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main_loop()