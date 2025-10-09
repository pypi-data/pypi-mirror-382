# Squirrely 🐿️

**Squirrely** は、ディレクトリ構成を Markdown 形式で生成する Python ツールです。  
好奇心旺盛なリスのキャラクター「Squirrely」をイメージしています。

---

## 特徴

- ディレクトリ構成をツリー形式で Markdown に出力
- CLI でも Python モジュールとしても利用可能
- 親しみやすく、教育やドキュメント作成にも活用できる

---

## インストール

```bash
pip install squirrely
```

---

## 使い方

CLI から実行

```bash
squirrely /path/to/your/project
```

生成例:

```markdown
## ディレクトリ構成

Project/
├── src/
│   ├── main/
│   └── test/
└── README.md
```

Python モジュールとして使用

```python
import squirrely

squirrely.main("C:/dir_path")
```
---

##  キャラクター
Squirrely は、好奇心旺盛で動き回るリスのキャラクターです。
今後、頻繁に使用するような機能を、あまり型枠にとらわれず柔軟に追加していく予定です。