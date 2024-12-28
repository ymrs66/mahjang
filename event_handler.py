import pygame
from events import handle_pon_click
from constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN, AI_ACTION_DELAY
from drawing import draw_pon_button  # ポンボタンの描画関数

def handle_events(state, current_time, screen):
    """
    イベントを処理してゲーム状態を更新する。
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # プレイヤーのターン
        if state.game.current_turn == 0:
            state.tsumo_tile, state.selected_tile = handle_player_input(
                event, state.game, state.tsumo_tile, state.selected_tile, current_time
            )
            if state.game.current_turn == 1:  # プレイヤーが牌を捨て終わりAIのターンに移行
                state.ai_action_time = current_time + AI_ACTION_DELAY

        # ポン待機フェーズ
        if state.game.current_turn == 3:
            handle_pon_phase(event, state, screen)

    return True

def handle_pon_phase(event, state, screen):
    """
    ポンが可能な状態での操作
    """
    if state.game.can_pon:
        pon_button_rect = draw_pon_button(screen, True)
        if handle_pon_click(event, pon_button_rect, state.game):  # ポンボタンがクリックされた場合
            print(f"ポンを実行: {state.game.target_tile}")
            state.game.process_pon(0)  # ポンの処理を実行
            state.game.can_pon = False
            state.game.current_turn = 2  # ツモフェーズに移行
            state.draw_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY
            debug_state(state, "ポン成功後の状態")
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # スペースキーでスキップ
            print("ポンをスキップしました")
            state.game.can_pon = False
            state.game.current_turn = 2  # ツモフェーズに移行
            state.draw_action_time = pygame.time.get_ticks() + AI_ACTION_DELAY

def handle_player_input(event, game, tsumo_tile, selected_tile, current_time):
    """
    プレイヤーの入力処理
    """
    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        for i, tile in enumerate(game.players[0].tiles):
            x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN)
            y = 500
            if x <= pos[0] <= x + TILE_WIDTH and y <= pos[1] <= y + TILE_HEIGHT:
                selected_tile = tile

        if tsumo_tile:
            x = TILE_WIDTH + len(game.players[0].tiles) * (TILE_WIDTH + TILE_MARGIN) + 20
            y = 500
            if x <= pos[0] <= x + TILE_WIDTH and y <= pos[1] <= y + TILE_HEIGHT:
                selected_tile = tsumo_tile

    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and selected_tile:
        # 捨て牌の処理
        if selected_tile == tsumo_tile:
            game.discards[0].append(tsumo_tile)
            tsumo_tile = None
        else:
            game.discards[0].append(selected_tile)
            game.players[0].remove_tile(selected_tile)

        # ツモ牌が存在する場合、手牌に追加してソート
        if tsumo_tile:
            game.players[0].add_tile(tsumo_tile)
            game.players[0].sort_tiles()
            tsumo_tile = None

        # プレイヤーのターン終了、AIのターンへ
        game.current_turn = 1

    return tsumo_tile, selected_tile

def debug_state(state, context):
    """
    ゲームの状態をデバッグ出力する。
    """
    print(f"=== デバッグ情報: {context} ===")
    print(f"現在のターン: {state.game.current_turn}")
    print(f"ポン可能フラグ: {state.game.can_pon}")
    print(f"ポン対象の牌: {state.game.target_tile}")
    print(f"手牌: {state.game.players[0].tiles}")
    print(f"AIの捨て牌: {state.game.discards[1]}")
    print(f"ツモ牌: {state.tsumo_tile}")
    print("=========================")