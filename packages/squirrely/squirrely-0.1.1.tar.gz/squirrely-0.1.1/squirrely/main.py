# cSpell:ignore squirrely
# squirrely/main.py

from .core import generate_tree, save_as_markdown

def main(target_dir: str = None):
    """
    Squirrelyのメイン関数
    """
    if target_dir is None:
        target_dir = input("対象ディレクトリを入力してください").strip()
    save_as_markdown(target_dir)