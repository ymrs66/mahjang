# core/resource_utils.py
from pathlib import Path
import sys

def get_resource_path(relative_path: str, *, must_exist: bool = True) -> str:
    """
    リソースの絶対パスを返す（PyInstaller 配布 & 通常実行の両対応）。
    - 開発時: このファイルの親ディレクトリ（= プロジェクトルート）を起点にする
    - 配布時: PyInstaller の展開先 (_MEIPASS) を起点にする
    - must_exist=True のとき存在しなければ FileNotFoundError
    """
    # 1) 配布物（凍結）かどうか
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        # core/ から 1 つ上（mahjang/）をルートとみなす
        base = Path(__file__).resolve().parents[1]

    # 2) 絶対パスへ正規化
    path = (base / relative_path).resolve()

    if must_exist and not path.exists():
        raise FileNotFoundError(f"リソースが見つかりません: {path}")
    return str(path)
