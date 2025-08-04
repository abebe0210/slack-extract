"""
Slack チャンネル一覧取得ユーティリティ
"""

import json
import os
from slack_api_collector import SlackAPICollector, load_config


def list_channels():
    """チャンネル一覧を取得して表示"""
    config = load_config()
    
    if not config:
        print("config.json が見つかりません。")
        print("config.example.json を参考に config.json を作成してください。")
        return
    
    token = config.get('slack_token')
    if not token or token == "xoxb-your-slack-bot-token-here":
        print("Slack Bot Token が設定されていません。")
        print("config.json の slack_token を正しく設定してください。")
        return
    
    # チャンネル一覧を取得
    collector = SlackAPICollector(token)
    channels = collector.get_channels()
    
    if not channels:
        print("チャンネルを取得できませんでした。")
        return
    
    print("=" * 80)
    print("利用可能なチャンネル一覧:")
    print("=" * 80)
    print(f"{'チャンネル名':<30} {'チャンネルID':<15} {'タイプ':<10} {'メンバー数'}")
    print("-" * 80)
    
    for channel in channels:
        name = channel.get('name', 'Unknown')
        channel_id = channel.get('id', 'Unknown')
        is_private = channel.get('is_private', False)
        channel_type = 'Private' if is_private else 'Public'
        member_count = channel.get('num_members', 0)
        
        print(f"{name:<30} {channel_id:<15} {channel_type:<10} {member_count}")
    
    print("\n" + "=" * 80)
    print("使用方法:")
    print("1. 上記のチャンネル一覧から収集したいチャンネルのIDをコピー")
    print("2. config.json の channel_ids 配列にチャンネルIDを追加")
    print("3. python slack_api_collector.py を実行してデータ収集")
    print("=" * 80)


if __name__ == "__main__":
    list_channels()
