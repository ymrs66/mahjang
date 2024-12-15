# events.py
import pygame  # pygame を明示的にインポート
from constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN

def handle_player_input(event, game, tsumo_tile, selected_tile, current_time):
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
        if selected_tile == tsumo_tile:
            game.discards[0].append(tsumo_tile)
            tsumo_tile = None
        else:
            game.discards[0].append(selected_tile)
            game.players[0].remove_tile(selected_tile)

        if tsumo_tile:
            game.players[0].add_tile(tsumo_tile)
            game.players[0].sort_tiles()
            tsumo_tile = None

        game.current_turn = 1

    return tsumo_tile, selected_tile