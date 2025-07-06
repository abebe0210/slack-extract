# channelsとusersのCSVを作成する
import pandas as pd
import json
import glob
from zipExtractor import ZipExtractor

def check_and_extract_zip():
    """ZIPファイルの存在チェックと解凍"""
    # ルートディレクトリとdataディレクトリの両方でZIPファイルを検索
    zip_files = glob.glob('*.zip') + glob.glob('data/*.zip')
    for zip_file in zip_files:
        if 'slack' in zip_file.lower() or 'export' in zip_file.lower():
            print(f"Slackエクスポートファイルを発見: {zip_file}")
            extractor = ZipExtractor(zip_file, 'data')
            extractor.extract_with_encoding_fix()
            break

# ZIPファイルが存在する場合は解凍処理を実行
check_and_extract_zip()

files = ['channels','users']

for filename in files:
  with open('data/' + filename +'.json', 'r', encoding='utf-8') as f:
      d = json.loads(f.read())

  df = pd.json_normalize(d, sep='_')
  if filename == 'users':
    df['display_name_custom'] = ""
    
    for index, row in df.iterrows():
        display_name_custom = row['name'] if row['profile_display_name_normalized'] == "" else row['profile_display_name_normalized']
        print(display_name_custom)
        df.at[index, 'display_name_custom'] = display_name_custom

  df.to_csv('output/' + filename +'.csv', encoding='utf_8_sig')
