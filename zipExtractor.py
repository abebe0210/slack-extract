import zipfile
import os
import shutil

class ZipExtractor:
    def __init__(self, zip_path, extract_to='data'):
        self.zip_path = zip_path
        self.extract_to = extract_to
    
    def extract_with_encoding_fix(self):
        """文字化けを修正してZIPファイルを解凍"""
        if not os.path.exists(self.zip_path):
            print(f"ZIPファイルが見つかりません: {self.zip_path}")
            return False
        
        # 解凍先ディレクトリが存在しない場合は作成
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)
        
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as myzip:
                infolist = myzip.infolist()
                
                for info in infolist:
                    try:
                        # cp437からutf-8に変換して文字化けを修正
                        filename_utf_8 = info.filename.encode('cp437').decode('utf-8')
                        
                        # ファイルを解凍
                        extracted_data = myzip.read(info)
                        
                        # 解凍先のパスを作成
                        extract_path = os.path.join(self.extract_to, filename_utf_8)
                        
                        # ディレクトリが存在しない場合は作成
                        extract_dir = os.path.dirname(extract_path)
                        if extract_dir and not os.path.exists(extract_dir):
                            os.makedirs(extract_dir)
                        
                        # ファイルでない場合（ディレクトリ）はスキップ
                        if not info.is_dir():
                            with open(extract_path, 'wb') as f:
                                f.write(extracted_data)
                    
                    except (UnicodeDecodeError, UnicodeEncodeError) as e:
                        print(f"文字化け修正失敗: {info.filename} - {e}")
                        # フォールバック: 元のファイル名で解凍
                        myzip.extract(info, self.extract_to)
            
            print(f"ZIPファイルの解凍が完了しました: {self.zip_path}")
            return True
            
        except Exception as e:
            print(f"ZIP解凍エラー: {e}")
            return False
