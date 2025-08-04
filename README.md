# Slack Analytics & Data Collector

SlackのエクスポートデータとAPIを使用したデータ収集・分析ツール

## 環境
- Windows
- Python 3.X

## 依存関係のインストール
```powershell
pip install -r requirements.txt
```

---

## 機能

### 1. Slack API データ収集（リアルタイム）

Slack APIを使用してリアルタイムでデータを収集し、CSV形式で出力します。

#### 必要な準備
1. **Slack App の作成とBot Token の取得**
   - [Slack API](https://api.slack.com/apps) でアプリを作成
   - OAuth & Permissions で以下のBot Token Scopesを追加:
     - `channels:history`
     - `channels:read`
     - `groups:history`
     - `groups:read`
     - `chat:write` (パーマリンク取得用)
   - Bot User OAuth Token (`xoxb-`で始まる) をコピー

#### 使用方法
1. **設定ファイルの作成**
   ```powershell
   Copy-Item config.example.json config.json
   ```

2. **設定の編集**
   - `config.json` を編集してSlack Bot Tokenとチャンネル情報を設定
   - または `.env` ファイルを作成してトークンを設定:
     ```
     SLACK_BOT_TOKEN=xoxb-your-actual-token-here
     ```

3. **チャンネル一覧の確認**
   ```powershell
   python list_channels.py
   ```

4. **データ収集の実行**
   ```powershell
   python slack_api_collector.py
   ```

#### 出力データ形式
`output/slack_data.csv` に以下の形式で出力されます：

| column_name | description |
|-------------|-------------|
| channel_id  | チャンネルID |
| talk_id     | メッセージのUUID（client_msg_idまたは生成されたUUID） |
| talk_user   | 投稿者のユーザーID |
| date        | 投稿日（YYYY-MM-DD） |
| ts          | タイムスタンプ |
| thread_ts   | スレッドのタイムスタンプ（親投稿特定用） |
| text        | 整形されたメッセージテキスト |
| url         | パーマリンク |

#### スレッド構造の理解
- **親投稿**: `thread_ts`が空または`ts`と同じ値
- **スレッドの返信**: `thread_ts`に親投稿の`ts`が設定される
- 同じ`thread_ts`を持つメッセージは同一スレッドに属する

#### テキスト整形機能
以下の整形が自動的に適用されます：
- `<!channel>`, `<!here>` の除去
- 絵文字記号（`:emoji_name:`）の除去
- 連続するスペース・タブの正規化（改行は保持）
- 各行の前後の空白除去

---

### 2. Slackエクスポートデータ処理（従来機能）

Slackの標準エクスポート機能で取得したZIPファイルを処理します。

#### 使用方法
1. Slackからログをダウンロード（設定と権限＞データのインポート／エクスポート）
2. ダウンロードしたZIPファイルをプロジェクトのルートディレクトリに配置
3. `python createMasterCsv.py` を実行（ZIPファイルが自動的に解凍されます）
4. `python createTalkCsv.py` を実行

#### 機能
- **ZIP自動解凍**: SlackエクスポートのZIPファイルを自動検出・解凍
- **文字化け対応**: ZIPファイル内の日本語ファイル名の文字化けを自動修正
- **メッセージ分析**: チャンネルごと日付ごとのログからメッセージ、リアクション、メンションCSVを作成

#### 出力ファイル
- `output/channels.csv` - チャンネル情報
- `output/users.csv` - ユーザー情報
- `output/talk.csv` - メッセージ
- `output/reaction.csv` - リアクション
- `output/mention.csv` - メンション
- `output/channel/` - チャンネル別分析結果

---

### 3. 分析・可視化

#### ネットワーク図作成
```powershell
python drawNetworkGraph.py  # Jupyter Notebook推奨
```
- メンション関係のネットワーク図を出力
- 発言Top50に限定（チャンネル内分析推奨）

#### 被リアクションランキング
```powershell
python makeReactionedRanking.py
```
- 被リアクション数によるメッセージランキングを作成

---

## 設定例

### config.json
```json
{
  "slack_token": "xoxb-your-slack-bot-token-here",
  "channel_ids": [
    "C1234567890",
    "C0987654321"
  ],
  "output_file": "slack_data.csv"
}
```

### .env
```
SLACK_BOT_TOKEN=xoxb-your-actual-token-here
```

---

## 注意事項
- API使用時はSlackのレート制限に注意
- エクスポートデータ処理時は、ZIPファイル名に「slack」または「export」が含まれる必要があります
- 手動でdataフォルダを作成する必要はありません（自動作成されます）

## フォーク元
https://github.com/yakipudding/slack-analytics をベースに機能拡張