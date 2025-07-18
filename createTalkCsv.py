# channelごと日付ごとのファイルを取得してCSV作成
# ※createMasterCsvを実行してから行うこと
import os
import pandas as pd
import json
import glob
import csv
import re
import uuid

class CreateTalkCsv:
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

    def exec(self):
        # 列定義
        talk_cols = ['channel_id', 'talk_id', 'ts', 'thread_ts', 'talk_user', 'text', 'date']
        talk_norequire_cols = ['subtype', 'thread_ts', 'reactions']
        reaction_cols = ['channel_id', 'talk_id', 'talk_user', 'reaction_user', 'emoji', 'date']
        mention_cols = ['channel_id', 'talk_id', 'talk_user', 'mention_user', 'date']

        # 初期化
        talks_all = []
        talk_reactions_all = []
        talk_mentions_all = []
        channel_talk_counts = []  # チャンネル別投稿件数を格納

        df_channels = pd.read_csv('output/channels.csv', encoding='utf_8_sig')
        # アーカイブ済は除外
        df_channels = df_channels[df_channels['is_archived'] == False ]

        for index, channel in df_channels.iterrows():
            channel_id = channel['id']
            channel_name = channel['name']

            # チャンネルフォルダ内の日別jsonファイル一覧を取得
            datefiles = glob.glob('data/' + channel_name + '/*.json')

            # 初期化
            talks = []
            talk_reactions = []
            talk_mentions = []

            # 日付ファイル別ループ
            for datefile in datefiles:
                # 日付ファイル取得 + 欠損値補完
                df = pd.read_json(datefile, encoding='utf-8').fillna("")

                # 日付
                date = os.path.splitext(os.path.basename(datefile))[0]

                # 要素がない場合は追加
                for col in talk_norequire_cols: 
                    if not col in df.columns:
                        df[col] = ""

                # メッセージのみ
                df = df[df['subtype'] == ""]

                # 1行ずつ
                for index, row in df.iterrows():
                    talk_id = str(uuid.uuid4()) 
                    talk_user = row['user']

                    # talk
                    #talk = [channel_id, talk_id, row['ts'], row['thread_ts'], talk_user, row['text'], date]
                    talk = [channel_id, talk_id, row.get('ts','N/A'), row.get('thread_ts','N/A'), talk_user, row.get('text','N/A'), date]
                    talks.append(talk)
                    talks_all.append(talk)

                    # reaction
                    if row['reactions'] != "":
                        reactions = row['reactions']
                        # name/users/user
                        for reaction in reactions:
                            emoji = reaction['name']
                            reaction_users = reaction['users']
                            for reaction_user in reaction_users:
                                talk_reaction = [ channel_id, talk_id, talk_user, reaction_user, emoji, date ]
                                talk_reactions.append(talk_reaction)
                                talk_reactions_all.append(talk_reaction)
                
                    # mention
                    if 'text' in row:
#                        mentions = re.findall('<@[0-9a-zA-Z_./?-]{9}>', row['text'])  # 修正箇所
                        mentions = re.findall(r'@U[0-9A-Z]{9}', row['text'])
                    else:
                        mentions = []  # 修正箇所

                    for mention in mentions:
                        mention_user = mention[1:]
                        talk_mention = [channel_id, talk_id, talk_user, mention_user, date]
                        talk_mentions.append(talk_mention)
                        talk_mentions_all.append(talk_mention)

            # チャンネル別投稿件数を記録
            channel_talk_counts.append([channel_name, len(talks)])

            self.outputCsv('output/channel/' + channel_name +'_talk', talk_cols, talks)
            self.outputCsv('output/channel/' + channel_name +'_reaction', reaction_cols, talk_reactions)
            self.outputCsv('output/channel/' + channel_name +'_mention', mention_cols, talk_mentions)

        self.outputCsv('output/talk', talk_cols, talks_all)
        self.outputCsv('output/reaction', reaction_cols, talk_reactions_all)
        self.outputCsv('output/mention', mention_cols, talk_mentions_all)
        
        # チャンネル別投稿件数をCSV出力
        channel_count_cols = ['channel_name', 'talk_count']
        # 投稿件数の多い順にソート
        channel_talk_counts.sort(key=lambda x: x[1], reverse=True)
        self.outputCsv('output/channel_talk_counts', channel_count_cols, channel_talk_counts)

createTalkCsv = CreateTalkCsv()
createTalkCsv.exec()