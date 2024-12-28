# 麻雀ゲームプロジェクト

## 概要
このプロジェクトは、Python と Pygame を使用したシンプルな麻雀ゲームです。

## フォルダ構成
mahjang/ 
├── core/ # ゲームのコアロジック
├── drawing/ # 描画関連 
├── events/ # イベント処理 
├── ai/ # AI ロジック 
├── tests/ # ユニットテスト 
└── main.py # エントリーポイント


## 必要な環境
- Python 3.10+
- Pygame 2.6.1

## 実行方法
```bash
python main.py

##テスト
python -m unittest discover -s tests
設定
設定は config.json で管理しています。
