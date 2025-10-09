import json
import pandas as pd

from io import BytesIO
from typing import Any, NamedTuple, Optional, Union
from enum import Enum

from csv import DictReader, DictWriter, writer as csv_writer, QUOTE_MINIMAL
from pyzipper import AESZipFile, WZ_AES, ZIP_DEFLATED

from robertcommonbasic.basic.data.utils import generate_object_id
from robertcommonbasic.basic.os.file import get_file_folder, rename_file, get_file_encoding
from robertcommonbasic.basic.os.path import create_dir_if_not_exist


class FileType(Enum):
    AES_ZIP = 'aes_zip'
    CSV = 'csv'
    JSON = 'json'
    Excel = 'excel'


class FileConfig(NamedTuple):
    PATH: Union[str, BytesIO]
    MODE: FileType
    NAME: Optional[str] = None
    PSW: Union[str, list] = None
    FORMAT: str = 'w+'  # r+ 读写  w+ 覆盖 a+ 追加 rb+ 二进制
    ENCODE: Optional[str] = 'UTF-8-SIG'     # 支持中文
    ENGINE: Optional[str] = None


class FileAccessor:

    def __init__(self, config: FileConfig):
        self.config = config

    def save(self, file_content: Any, file_mode: str = 'w+'):
        create_dir_if_not_exist(get_file_folder(self.config.PATH))

        if self.config.MODE == FileType.AES_ZIP:
            return self.__save_aes_zip(self.config.PATH, self.config.NAME, file_content, self.config.PSW)
        elif self.config.MODE == FileType.CSV:
            return self.__save_csv_file(self.config.PATH, file_content, file_mode, self.config.ENCODE)
        elif self.config.MODE == FileType.JSON:
            return self.__save_json_file(self.config.PATH, file_content, file_mode, self.config.ENCODE)
        elif self.config.MODE == FileType.Excel:
            return self.__save_excel_file(self.config.PATH, file_content, self.config.ENCODE)

    def gen_temp_path(self, zip_path: str) -> str:
        return f"{zip_path}.{generate_object_id()}.tmp"

    def __save_aes_zip(self, zip_path: str, file_name: str, file_content: Any, zip_pw: Any = None):
        tmp_path = self.gen_temp_path(zip_path)
        with AESZipFile(tmp_path, 'a', compression=ZIP_DEFLATED) as zip_file:
            if isinstance(zip_pw, str) and len(zip_pw) > 0:
                zip_file.setpassword(zip_pw.encode('utf-8'))
            zip_file.setencryption(WZ_AES, nbits=256)
            if isinstance(file_content, str):
                zip_file.writestr(file_name, data=file_content)
        rename_file(tmp_path, zip_path)

    def __save_csv_file(self, file_path: str, file_content: Any, file_mode: str = 'w+', encoding: str = 'utf-8', newline: str = ''):
        tmp_path = self.gen_temp_path(file_path)
        with open(tmp_path, mode=file_mode, encoding=encoding) as f:
            if isinstance(file_content, str):
                f.write(file_content)
            elif isinstance(file_content, bytes):
                f.write(file_content)
            elif isinstance(file_content, list):
                for content in file_content:
                    f.write(content)
        rename_file(tmp_path, file_path)

    def __save_json_file(self, file_path: str, file_content: Any, file_mode: str = 'w+', encoding: str = 'utf-8', newline: str = ''):
        tmp_path = self.gen_temp_path(file_path)
        with open(tmp_path, mode=file_mode, encoding=encoding, newline=newline) as f:
            writer = DictWriter(f, fieldnames=file_content[0].keys())
            writer.writeheader()
            for row in file_content:
                writer.writerow(row)
        rename_file(tmp_path, file_path)

    def __save_excel_file(self, file_path: str, file_content: Any, encoding: str = 'utf-8'):
        tmp_path = self.gen_temp_path(file_path)
        if isinstance(file_content, dict):
            excel_writer = pd.ExcelWriter(tmp_path, engine='xlsxwriter')
            for k, v in file_content.items():
                pd.DataFrame(v).to_excel(excel_writer, sheet_name=k, index=False, encoding=encoding)
            excel_writer.save()
        rename_file(tmp_path, file_path)

    def read(self):
        if self.config.MODE == FileType.AES_ZIP:
            return self.__read_aes_zip(self.config.PATH, self.config.NAME, self.config.PSW)
        elif self.config.MODE == FileType.CSV:
            return self.__read_csv_dict(self.config.PATH)
        elif self.config.MODE == FileType.JSON:
            return self.__read_json_dict(self.config.PATH)
        elif self.config.MODE == FileType.Excel:
            return self.__read_excel_dict(self.config.PATH, self.config.NAME, self.config.ENGINE)

    def __read_aes_zip(self, zip_path: str, file_name: str = '', zip_pw: Any = None) -> dict:
        results = {}
        with AESZipFile(zip_path) as zip_file:
            psws = []
            if isinstance(zip_pw, str) and len(zip_pw) > 0:
                psws.append(zip_pw.encode('utf-8'))
            elif isinstance(zip_pw, list):
                for pw in zip_pw:
                    psws.append(pw.encode('utf-8'))
            else:
                psws = [None]

            if file_name is not None and len(file_name) > 0:
                for psw in psws:
                    try:
                        results[file_name] = zip_file.read(file_name, psw)
                        break
                    except Exception as e:
                        if e.__str__().find('password') >= 0:
                            continue
                        else:
                            raise e
            else:
                for file in zip_file.namelist():
                    for psw in psws:
                        try:
                            results[file] = zip_file.read(file, psw)
                            break
                        except Exception as e:
                            if e.__str__().find('password') >= 0:
                                continue
                            else:
                                raise e
        return results

    def __read_csv_dict(self, file_path: str, newline: str = ''):
        with open(file_path, newline=newline, encoding=get_file_encoding(file_path)) as file:
            reader = DictReader(file)
            return [row for row in reader]

    def __read_excel_dict(self, file_path: str, sheet_name: Optional[str] = None, engine: str = 'openpyxl') -> dict:
        df = pd.read_excel(file_path, engine=engine, sheet_name=sheet_name)
        records = {}
        if isinstance(df, dict):
            for name, _df in df.items():
                records[name] = [{k: v for k, v in v1.items() if v == v and v is not None} for k1, v1 in _df.T.to_dict().items()]
                del _df
        else:
            records[sheet_name] = [
                {k: v for k, v in v1.items() if v == v and v is not None} for k1, v1 in df.T.to_dict().items()
            ]
            del df
        return records

    def __write_csv_row(self, file_path: str, rows: list, file_mode: str = 'w', newline: str = ''):
        with open(file_path, file_mode, newline=newline) as file:
            writer = csv_writer(file, delimiter=' ', quotechar='|', quoting=QUOTE_MINIMAL)
            for row in rows:
                writer.writerow(row)

    def __write_csv_dict(self, file_path: str, rows: dict, file_mode: str = 'w', newline: str = ''):
        with open(file_path, file_mode, newline=newline) as file:
            writer = DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def __read_json_dict(self, file_path: str):
        with open(file_path) as file:
            return json.loads(file.read())
