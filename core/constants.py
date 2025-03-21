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
DRAWN_TILE_EXTRA_OFFSET = 20 #ツモ牌用の追加オフセット

# フェーズ
PLAYER_DISCARD_PHASE = 0  # プレイヤーの捨てるフェーズ
PLAYER_DRAW_PHASE = 1     # プレイヤーのツモフェーズ
AI_DRAW_PHASE = 2         # AIのツモフェーズ
AI_DISCARD_PHASE = 3      # AIの捨て牌フェーズ
MELD_WAIT_PHASE = 4  # ポンチーカンウェイトフェーズ
AI_ACTION_SELECTION_PHASE = 7  # AIのアクション選択フェーズ
PLAYER_ACTION_SELECTION_PHASE = 8  # プレイヤーのアクション選択フェーズ
PLAYER_SELECT_TILE_PHASE = 9 #牌選択フェーズ
WIN_RESULT_PHASE = 10      # 和了結果表示フェーズ
GAME_END_PHASE = 11        # ゲーム終了フェーズ