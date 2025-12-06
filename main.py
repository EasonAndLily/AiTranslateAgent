import os.path
import time
from pathlib import Path

from ai_translate import AiTranslate
from config import config
from excel_operator import ExcelOperator


if __name__ == "__main__":
    current_folder = Path(__file__).resolve().parent
    file_path = os.path.join(current_folder, config.file_name)
    print(f'待翻译的文件为：{file_path}')
    with ExcelOperator(file_path) as eop:
        vals = eop.read_column(sheet_name=config.translate_sheet_name, column=config.translate_sheet_column,
                               skip_header=True, skip_empty=True)
        print(f'已读取文件【{config.file_name}】里面【{config.translate_sheet_name}】的待翻译内容')
        new_sheet = f'{config.translate_sheet_name}_{config.target_language}'
        eop.create_sheet(new_sheet)
        print(f'已创建新的Sheet：{new_sheet}')

        for i in range(0, len(vals), config.batch_size):
            print(f'开始批量翻译，批量翻译数据：{config.batch_size} 条')
            translate = AiTranslate(config, vals[i:i + config.batch_size])
            results = translate.translate_to()
            print(f'批量翻译成功，翻译结果为：{results}')
            eop.write_columns(
                new_sheet,
                {
                    "A": vals[i:i + config.batch_size],
                    "B": results,
                },
                start_row=i + 1,
                clear_first=True,
                save=True
            )
            print(f'批量翻译的结果已经写入到新建sheet: {new_sheet} 里面')
            time.sleep(2)
