# drawing.py
import pygame
from constants import TILE_WIDTH, TILE_HEIGHT, TILE_MARGIN, TILE_MARGIN_AI

def draw_tiles(screen, hand, tsumo_tile, selected_tile):
    screen.fill((255, 255, 255))  # 背景を白で塗りつぶす
    for i, tile in enumerate(hand.tiles):
        x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN)
        y = 500
        screen.blit(tile.image, (x, y))
        if tile == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_WIDTH, TILE_HEIGHT), 3)

    if tsumo_tile:
        x = TILE_WIDTH + len(hand.tiles) * (TILE_WIDTH + TILE_MARGIN) + 20
        y = 500
        screen.blit(tsumo_tile.image, (x, y))
        if tsumo_tile == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, TILE_WIDTH, TILE_HEIGHT), 3)

def draw_ai_tiles(screen):
    for i in range(13):
        x = TILE_WIDTH + i * (TILE_WIDTH + TILE_MARGIN_AI)
        y = 50
        ura_image = pygame.image.load("images/ura.png")
        screen.blit(ura_image, (x, y))

def draw_discards(screen, discards):
    for i, tile in enumerate(discards[0]):
        x = 200 + (i % 10) * (TILE_WIDTH + TILE_MARGIN)
        y = 300 + (i // 10) * (TILE_HEIGHT + TILE_MARGIN)
        screen.blit(tile.image, (x, y))

    for i, tile in enumerate(discards[1]):
        x = 850 - (i % 10) * (TILE_WIDTH + TILE_MARGIN)
        y = 150 + (i // 10) * (TILE_HEIGHT + TILE_MARGIN)
        rotated_image = pygame.transform.rotate(tile.image, 180)
        screen.blit(rotated_image, (x, y))