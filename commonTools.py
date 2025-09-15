# channelごと日付ごとのファイルを取得してCSV作成
# ※createMasterCsvを実行してから行うこと
import os
import pandas as pd
import json
import glob
import csv
import re
import uuid
from datetime import datetime

def _slugify(name: str) -> str:
    # ファイル名に使えない文字を置換
    return re.sub(r"[^\w\-_.]+", "_", name).strip("._")

def get_run_id_from_zip(zip_path: str) -> str:
    """ZIPファイルパスからrun_idを生成（拡張子除去・サニタイズ）"""
    base = os.path.basename(zip_path)
    root, _ = os.path.splitext(base)
    return _slugify(root)

def ensure_dir(path: str):
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def get_data_dir(run_id: str) -> str:
    return os.path.join('data', run_id) if run_id else 'data'

def get_output_dir(run_id: str) -> str:
    return os.path.join('output', run_id) if run_id else 'output'

def list_run_ids(base: str = 'output') -> list:
    """指定ベース配下のrun_idディレクトリ一覧を返す"""
    if not os.path.isdir(base):
        return []
    return sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))])

def get_latest_run_id(base: str = 'output') -> str | None:
    """更新が新しい順に最後の実行ディレクトリを返す"""
    if not os.path.isdir(base):
        return None
    dirs = [(d, os.path.getmtime(os.path.join(base, d))) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
    if not dirs:
        return None
    dirs.sort(key=lambda x: x[1], reverse=True)
    # 最も新しい更新時刻のディレクトリ名を返す
    return dirs[0][0]

class CommonTools:
    def outputCsv(self, filename, header, contents):
        write_encoding = 'utf_8_sig' #excelとかで見るからbom付ける
        # ディレクトリが存在しない場合は作成
        dir_path = os.path.dirname(filename + '.csv')
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(filename + '.csv', 'w', encoding=write_encoding) as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(header)
            writer.writerows(contents)

    def convertTalkText(self, text, df_users):
        #df_usersのindexはuser_idにすること
        #emojiは変換しません
        repDict = {
            '<!here>': '`@here`',
            '<!channel>': '`@channel`'
        }
        #ユーザーメンションの置換
        mentions = re.findall('<@[0-9a-zA-Z_./?-]{9}>', text)
        for mention in mentions:
            mention_user = mention[2:-1]
            mention_user_name = df_users.at[mention_user,'display_name_custom']
            if mention_user not in repDict:
                repDict[mention] = '`@' + mention_user_name + '`'
        
        for key, value in repDict.items():
            text = text.replace(key, value)

        return text
        

