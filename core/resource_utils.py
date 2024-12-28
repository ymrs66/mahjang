##resource_utils.py
import os

def get_resource_path(path):
    """
    指定されたリソースパスが存在する場合、そのパスを返す。
    存在しない場合は None を返す。
    """
    if os.path.exists(path):
        return path
    print(f"リソースが見つかりません: {path}")
    return None