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
# main.py
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

        # AIが牌を捨てる処理
        if game.current_turn == 1 and current_time >= ai_action_time:
            discard_tile = game.players[1].discard_tile()  # AIが牌を捨てる
            if discard_tile is not None:
                game.discards[1].append(discard_tile)

                # ポンの条件をチェック
                if game.check_pon(0, discard_tile):  # プレイヤーのポンをチェック
                    print(f"ポン可能: {discard_tile}")  # デバッグ用ログ
                    game.current_turn = 3  # ポン待機状態に設定
                else:
                    game.current_turn = 2  # プレイヤーのツモに移行
            else:
                print("AIが捨てる牌がありません！")  # デバッグ用ログ
                game.current_turn = 2  # ツモに移行

            ai_action_time = current_time + AI_ACTION_DELAY

        # プレイヤーのツモ処理
        if game.current_turn == 2 and current_time >= ai_action_time:
            tsumo_tile = game.draw_tile(0)
            game.current_turn = 0

        # ポン待機状態の処理
        if game.current_turn == 3:
            for event in pygame.event.get():
                if handle_pon_click(event, game, pon_button_rect):  # ポンボタンがクリックされた場合
                    print("ポン処理を実行")
                    # ポン処理の実行コードをここに追加
                    game.current_turn = 2  # プレイヤーのツモフェーズに移行
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # スペースキーでポンを無視
                    print("ポンを無視")
                    game.current_turn = 2  # ツモフェーズに移行

        if game.can_pon:
            if handle_pon_click(event, pon_button_rect, game):
                game.can_pon = False  # ポン状態をリセット
                game.current_turn = 0  # プレイヤーの捨て牌フェーズに移行
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game.can_pon = False  # ポン状態をリセット
                game.current_turn = 2  # ツモフェーズに移行

        # 描画
        draw_tiles(screen, game.players[0], tsumo_tile, selected_tile)
        draw_ai_tiles(screen)
        draw_discards(screen, game.discards)

        # ポンボタンの描画 (最後に描画)
        if game.can_pon:
            pon_button_rect = draw_pon_button(screen, True)
        else:
            pon_button_rect = None
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main_loop()