# 牌を表現するクラス
# tile.py
import pygame
from core.resource_utils import get_resource_path

class Tile:
    def __init__(self, suit, value, image_path=None):
        """
        suit: 牌の種類 ('m', 'p', 's', 'z')
        value: 数字または字牌 ('1', ..., '9', '東', '南', '白', '發', '中')
        image_path: 画像ファイルのパス (None の場合は画像はロードされない)
        """
        self.suit = suit  # 牌の種類
        self.value = value  # 数字または字牌
        self.image = None  # 初期値として None を設定
        self.is_riichi_discard = False   # ← リーチ捨て牌フラグを初期Falseに
        self.is_meld_discard = False

        if image_path:  # 画像パスが指定されている場合のみ画像をロード
            abs_path = get_resource_path(image_path)  # ★ここで絶対パス化
            if abs_path is None:
                raise FileNotFoundError(f"画像が見つかりません: {image_path}")
            self.image = pygame.image.load(abs_path)

    def is_same_tile(self, other):
        """
        suit と value が同じであれば True を返す比較メソッド。
        カンの判定などに利用する。
        """
        if isinstance(other, Tile):
            return self.suit == other.suit and self.value == other.value
        return False

    def __repr__(self):
        """
        オブジェクトの文字列表現を返す (デバッグ用)。
        """
        return f"{self.value}{self.suit} (id={id(self)})"