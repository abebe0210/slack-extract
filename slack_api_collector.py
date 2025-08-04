"""
Slack API を使用してデータを収集し、CSV形式で出力するプログラム
"""

import os
import csv
import json
import time
import re
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional
import requests
import logging
from dotenv import load_dotenv

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SlackAPICollector:
    def __init__(self, token: str):
        """
        Slack API コレクター初期化
        
        Args:
            token (str): Slack Bot Token (xoxb-で始まる)
        """
        self.token = token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Slack API リクエストを実行"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            logger.error(f"HTTP Error: {response.status_code}")
            return {}
            
        data = response.json()
        if not data.get('ok'):
            logger.error(f"API Error: {data.get('error')}")
            return {}
            
        return data
    
    def get_channels(self, types: str = "public_channel,private_channel") -> List[Dict]:
        """チャンネル一覧を取得"""
        channels = []
        cursor = None
        
        while True:
            params = {"types": types, "limit": 200}
            if cursor:
                params["cursor"] = cursor
                
            data = self._make_request("conversations.list", params)
            if not data:
                break
                
            channels.extend(data.get("channels", []))
            cursor = data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
                
            time.sleep(1)
            
        return channels
    
    def get_channel_history(self, channel_id: str, oldest: str = None, latest: str = None) -> List[Dict]:
        """チャンネルの履歴を取得"""
        messages = []
        cursor = None
        
        while True:
            params = {"channel": channel_id, "limit": 200}
            if oldest:
                params["oldest"] = oldest
            if latest:
                params["latest"] = latest
            if cursor:
                params["cursor"] = cursor
                
            data = self._make_request("conversations.history", params)
            if not data:
                break
                
            messages.extend(data.get("messages", []))
            cursor = data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
                
            time.sleep(1)
            
        return messages
    
    def get_thread_replies(self, channel_id: str, thread_ts: str) -> List[Dict]:
        """スレッドの返信を取得"""
        params = {"channel": channel_id, "ts": thread_ts}
        data = self._make_request("conversations.replies", params)
        return data.get("messages", []) if data else []
    
    def get_permalink(self, channel_id: str, message_ts: str) -> str:
        """メッセージのパーマリンクを取得"""
        params = {"channel": channel_id, "message_ts": message_ts}
        data = self._make_request("chat.getPermalink", params)
        return data.get("permalink", "") if data else ""
    
    def format_text(self, text: str) -> str:
        """テキストを整形"""
        if not text:
            return ""
        
        # <!channel>, <!here>の除去
        text = re.sub(r'<!channel>', '', text)
        text = re.sub(r'<!here>', '', text)
        
        # 絵文字記号の除去
        text = re.sub(r':[a-zA-Z0-9_\-+]+:', '', text)
        
        # 連続するスペース・タブを単一スペースに（改行は保持）
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 各行の前後の空白を除去
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines).strip()
        
        return text
    
    def collect_channel_data(self, channel_ids: List[str], output_file: str = "slack_data.csv"):
        """指定されたチャンネルのデータを収集してCSVに出力"""
        logger.info("データ収集を開始します")
        
        os.makedirs("output", exist_ok=True)
        output_path = os.path.join("output", output_file)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['channel_id', 'talk_id', 'talk_user', 'date', 'ts', 'thread_ts', 'text', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for channel_id in channel_ids:
                logger.info(f"チャンネル {channel_id} のデータを収集中...")
                messages = self.get_channel_history(channel_id)
                
                for message in messages:
                    row_data = self._process_message(channel_id, message)
                    if row_data:
                        writer.writerow(row_data)
                    
                    # スレッド返信の処理
                    if message.get('thread_ts') and message.get('reply_count', 0) > 0:
                        thread_replies = self.get_thread_replies(channel_id, message['ts'])
                        for reply in thread_replies[1:]:
                            reply_data = self._process_message(channel_id, reply)
                            if reply_data:
                                writer.writerow(reply_data)
                
                time.sleep(2)
        
        logger.info(f"データ収集完了: {output_path}")
    
    def _process_message(self, channel_id: str, message: Dict) -> Optional[Dict]:
        """メッセージデータを処理してCSV行データを作成"""
        # システムメッセージを除外
        if message.get('subtype') in ['bot_message', 'channel_join', 'channel_leave']:
            return None
        
        ts = message.get('ts', '')
        thread_ts = message.get('thread_ts', '')
        text = message.get('text', '')
        user_id = message.get('user', '')
        
        # talk_idの生成
        talk_id = message.get('client_msg_id') or str(uuid.uuid5(
            uuid.NAMESPACE_DNS, f"{ts}_{user_id}_{channel_id}"
        ))
        
        # 日付の作成
        try:
            dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
            date = dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            date = ''
        
        return {
            'channel_id': channel_id,
            'talk_id': talk_id,
            'talk_user': user_id,
            'date': date,
            'ts': ts,
            'thread_ts': thread_ts,
            'text': self.format_text(text),
            'url': self.get_permalink(channel_id, ts)
        }


def load_config() -> Dict:
    """設定ファイルを読み込み"""
    load_dotenv()
    
    config_file = "config.json"
    if not os.path.exists(config_file):
        template_config = {
            "slack_token": "xoxb-your-slack-bot-token-here",
            "channel_ids": ["C1234567890", "C0987654321"],
            "output_file": "slack_data.csv"
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"設定ファイル {config_file} を作成しました。設定を編集してから再実行してください。")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 環境変数からトークンを取得（設定ファイルより優先）
        env_token = os.getenv('SLACK_BOT_TOKEN')
        if env_token:
            config['slack_token'] = env_token
            
        return config
    except json.JSONDecodeError as e:
        logger.error(f"設定ファイルの読み込みエラー: {e}")
        return {}


def main():
    """メイン実行関数"""
    config = load_config()
    
    if not config:
        logger.error("設定ファイルが見つかりません")
        return
    
    token = config.get('slack_token')
    channel_ids = config.get('channel_ids', [])
    output_file = config.get('output_file', 'slack_data.csv')
    
    if not token or token == "xoxb-your-slack-bot-token-here":
        logger.error("Slack token が設定されていません")
        return
    
    if not channel_ids:
        logger.error("収集対象のチャンネルIDが設定されていません")
        return
    
    collector = SlackAPICollector(token)
    collector.collect_channel_data(channel_ids, output_file)


if __name__ == "__main__":
    main()
