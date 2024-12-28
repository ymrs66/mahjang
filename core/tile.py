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
    def __init__(self, suit, value, image_path=None):
        self.suit = suit  # 牌の種類
        self.value = value  # 数字または字牌
        self.image = None  # 初期値として None を設定

        if image_path:  # 画像パスが指定されている場合のみ画像をロード
            self.image = pygame.image.load(image_path)

    def __eq__(self, other):
        if isinstance(other, Tile):
            return self.suit == other.suit and self.value == other.value
        return False

    def __repr__(self):
        # 例: '1m', '5p', '中'
        return f"{self.value}{self.suit} (id={id(self)})"