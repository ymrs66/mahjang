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

## License

- **Code**: PolyForm Noncommercial 1.0.0 (see `LICENSE`)
- **Assets (images/fonts)**: CC BY-NC 4.0 (see `LICENSE-ASSETS`)

### You can
- 非商用の目的に限り、コードを利用・学習・改変できます  
- 非商用の目的に限り、コードおよび派生物を**再配布**できます（ライセンス本文と著作権表示を同梱してください）  
- 本リポジトリへの **Pull Request を目的とする公開フォーク**を作れます

### You cannot
- コード/アセットを**商用目的**で利用・配布できません（販売・SaaS提供・広告収益を得る配布等を含む）  
- ライセンスや著作権表示を削除できません  
- ロゴや名称などの商標権は付与されません

> 非商用の定義や条件は `LICENSE`（PolyForm Noncommercial 1.0.0）の本文をご確認ください。

