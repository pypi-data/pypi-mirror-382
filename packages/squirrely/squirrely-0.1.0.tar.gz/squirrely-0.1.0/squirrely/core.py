# cSpell:ignore squirrely
# squirrely/main.py

import os

def generate_tree(path: str, prefix: str = "") -> str:
    entries = sorted(os.listdir(path))
    tree_str = ""
    for index, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if index == len(entries) - 1 else "├── "
        tree_str += f"{prefix}{connector}{entry}\n"
        if os.path.isdir(full_path):
            extension = "    " if index == len(entries) - 1 else "│   "
            tree_str += generate_tree(full_path, prefix + extension)
    return tree_str

def save_as_markdown(root_dir: str, output_file: str = "ディレクトリ構成.md") -> None:
    tree_text = f"## ディレクトリ構成\n\n{os.path.basename(root_dir)}/\n"
    tree_text += generate_tree(root_dir)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tree_text)
    print(f"Markdown出力完了：{output_file}")
