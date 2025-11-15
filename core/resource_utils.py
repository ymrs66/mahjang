##resource_utils.py
import sys
import os

def get_resource_path(relative_path):
    """
    PyInstaller対応: リソースファイルの絶対パスを返す。
    通常実行時はカレントディレクトリ、PyInstaller実行時は展開先から取得。
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    path = os.path.join(base_path, relative_path)
    if os.path.exists(path):
        return path
    print(f"リソースが見つかりません: {path}")
    return None 