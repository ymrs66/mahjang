# 牌を表現するクラス
# tile.py
import pygame

class Tile:
    def __init__(self, suit, value, image_path):
        """
        suit: 牌の種類 ('m', 'p', 's', 'z')
        value: 数字または字牌 ('1', ..., '9', '東', '南', '白', '發', '中')
        image_path: 画像ファイルのパス
        """
        self.suit = suit
        self.value = value
        self.image = pygame.image.load(image_path)  # 画像を読み込み

    def __repr__(self):
        # 例: '1m', '5p', '中'
        return f"{self.value}{self.suit} (id={id(self)})"