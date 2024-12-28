## constants.py

# タイル描画のサイズとマージン
TILE_WIDTH = 40
TILE_HEIGHT = 60
TILE_MARGIN = 5
TILE_MARGIN_AI = 5

# 画像リソース
AI_TILE_BACK_IMAGE = "drawing/images/ura.png"
TILE_IMAGE_PATH = "drawing/images/{value}{suit}.png"

# 牌
SUITS = ['m', 'p', 's']
HONORS = ['ton', 'nan', 'sha', 'pe', 'haku', 'hatsu', 'chun']

# フォントリソース
DEFAULT_FONT_PATH = "fonts/meiryo.ttc"
BOLD_FONT_PATH = "fonts/meiryob.ttc"

# 画面サイズ
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 700
AI_ACTION_DELAY = 1000  # AI のアクション待機時間（ミリ秒）

# ポン表示のオフセット
PON_OFFSET_X = 100  # 右方向へのオフセット
PON_OFFSET_Y = 450  # 基準となるY座標