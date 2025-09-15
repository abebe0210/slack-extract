# channelsとusersのCSVを作成する
import pandas as pd
import json
import glob
import os
from zipExtractor import ZipExtractor
import commonTools

def check_and_extract_zip():
    """ZIPファイルの存在チェックと解凍（複数ZIP対応）"""
    # ルートディレクトリとdataディレクトリの両方でZIPファイルを検索
    zip_files = glob.glob('*.zip') + glob.glob('data/*.zip')
    for zip_file in zip_files:
        if 'slack' in zip_file.lower() or 'export' in zip_file.lower():
            run_id = commonTools.get_run_id_from_zip(zip_file)
            data_dir = commonTools.get_data_dir(run_id)
            print(f"Slackエクスポートファイルを発見: {zip_file} -> run_id={run_id}")
            extractor = ZipExtractor(zip_file, data_dir)
            extractor.extract_with_encoding_fix()

# ZIPファイルが存在する場合は解凍処理を実行（複数ある場合はすべて）
check_and_extract_zip()

# data配下のrun_idディレクトリを列挙
data_base = 'data'
run_ids = [d for d in os.listdir(data_base) if os.path.isdir(os.path.join(data_base, d))]
if not run_ids and os.path.isfile(os.path.join(data_base, 'channels.json')):
        # 旧仕様のフラット配置に対応（互換性）
        run_ids = [""]

files = ['channels','users']

for run_id in run_ids:
    data_dir = commonTools.get_data_dir(run_id) if run_id else 'data'
    out_dir = commonTools.get_output_dir(run_id) if run_id else 'output'
    os.makedirs(out_dir, exist_ok=True)
    for filename in files:
        with open(os.path.join(data_dir, filename +'.json'), 'r', encoding='utf-8') as f:
                d = json.loads(f.read())

        df = pd.json_normalize(d, sep='_')
        if filename == 'users':
            df['display_name_custom'] = ""
            for index, row in df.iterrows():
                    display_name_custom = row['name'] if row.get('profile_display_name_normalized', "") == "" else row['profile_display_name_normalized']
                    df.at[index, 'display_name_custom'] = display_name_custom

        df.to_csv(os.path.join(out_dir, filename +'.csv'), encoding='utf_8_sig', index=False)
