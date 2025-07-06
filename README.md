# slack-analytics

フォーク元: https://github.com/yakipudding/slack-analyticsをベースに機能拡張

## 環境
- Windows
- Python3.X

## ログ加工　使い方
1. Slackからログをダウンロードする（設定と権限＞データのインポート／エクスポート）
2. ダウンロードしたZIPファイルをプロジェクトのルートディレクトリに配置
3. createMasterCsv.pyを実行（ZIPファイルが自動的に解凍されます）
4. createTalkCsv.pyを実行

### 注意事項
- ZIPファイルのファイル名に「slack」または「export」が含まれている場合、自動的に`data`フォルダに解凍されます
- ZIPファイルの文字化け問題も自動的に修正されます
- 手動でdataフォルダを作成して解凍する必要はありません

## 新機能
- **ZIP自動解凍機能**: SlackエクスポートのZIPファイルを自動検出・解凍
- **文字化け対応**: ZIPファイル内の日本語ファイル名の文字化けを自動修正

## createMasterCsv.py
channels.json、users.jsonからcsv作成
- ZIPファイルの自動解凍機能付き
- output
	- channels.csv
	- users.csv

## createTalkCsv.py
チャンネルごと日付ごとのログからメッセージ、リアクション、メンションcsvを作成
- output
	- talk.csv
	- reaction.csv
	- mention.csv
	- チャンネル名ディレクトリ
		- talk.csv
		- reaction.csv
		- mention.csv

### メッセージ
|channel_id|talk_id|talk_user|text|
|:--|:--|:--|:--|
|C5XXXXXXX|XX1|U9XXXXXXX|`<@U8YYYYYYY>`こんにちは|
|C5XXXXXXX|XX2|U8YYYYYYY|帰りたい|
|C5XXXXXXX|XX3|U9XXXXXXX|しごおわ|

### リアクション
|channel_id|talk_id|talk_user|reaction_user|emoji|
|:--|:--|:--|:--|:--|
|C5XXXXXXX|XX1|U9XXXXXXX|U8YYYYYYY|ok_woman|
|C5XXXXXXX|XX1|U9XXXXXXX|U7ZZZZZZZ|iine|
|C5XXXXXXX|XX2|U8YYYYYYY|U9XXXXXXX|wakaru|
|C5XXXXXXX|XX2|U9XXXXXXX|U7ZZZZZZZ|otukare|

### メンション
|channel_id|talk_id|talk_user|mention_user|
|:--|:--|:--|:--|
|C5XXXXXXX|XX1|U9XXXXXXX|U8YYYYYYY|

## グラフ作成　使い方

### drawNetworkGraph.py
- Jupyter Notebookにメンション関係のネットワーク図を出力します
- 発言Top50に限定しているのでチャンネル内で分析するのをお勧めします
- ログ加工を先に実行しておくこと