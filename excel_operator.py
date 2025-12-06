from typing import List, Optional, Union, Dict, Iterable, Any
from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string
from openpyxl.worksheet.worksheet import Worksheet


class ExcelOperator:

    def __init__(self, filepath: str, read_only: bool = False):
        """
        :param filepath: Excel 文件路径 (.xlsx)
        :param read_only: 是否以 read_only 模式打开（大文件可用）
        """
        self.filepath = filepath
        self.read_only = read_only
        self.wb = None
        self._open_workbook()

    def close(self):
        """关闭工作簿（如果打开）。"""
        if self.wb:
            try:
                self.wb.close()
            except Exception:
                pass
            self.wb = None

    def read_column(
            self,
            sheet_name: str,
            column: Union[int, str],
            skip_header: bool = False,
            start_row: int = 1,
            end_row: Optional[int] = None,
            skip_empty: bool = True,
            values_only: bool = True
    ) -> List:
        """
        读取指定 sheet 的某个列到列表。

        :param sheet_name: sheet 名称
        :param column: 列标识，可以是列字母（"A"）、也可以是 1 起始的列索引（int）
        :param skip_header: 若 True，则跳过第一行（默认 False）
        :param start_row: 起始行（默认 1），skip_header=True 时会在此基础上再跳过一行
        :param end_row: 结束行（包含），默认 None 表示遍历到 sheet 末尾
        :param skip_empty: 若 True，则过滤掉 None 或 空字符串的单元格
        :param values_only: 是否只返回单元格的值（True），否则返回 Cell 对象（False）
        :return: 列值的列表
        """
        if self.wb is None:
            self._open_workbook()

        if sheet_name not in self.wb.sheetnames:
            raise KeyError(f"Sheet '{sheet_name}' 不存在。可用 sheets: {self.wb.sheetnames}")

        ws = self.wb[sheet_name]

        # 解析列索引
        if isinstance(column, str):
            try:
                col_idx = column_index_from_string(column)
            except Exception:
                raise ValueError(f"无效的列字母: {column}")
        elif isinstance(column, int):
            if column < 1:
                raise ValueError("列索引应为从 1 开始的正整数")
            col_idx = column
        else:
            raise TypeError("column 参数必须为列字母 (str) 或 1 起始的列索引 (int)")

        # 计算实际起始行
        actual_start = start_row
        if skip_header:
            actual_start = max(actual_start, start_row + 1)

        # 使用 iter_rows 高效读取单列
        values = []
        for col in ws.iter_cols(min_col=col_idx, max_col=col_idx,
                                min_row=actual_start, max_row=end_row,
                                values_only=values_only):
            # iter_cols 返回的是一个 tuple，包含该列指定区间的单元格或值
            for v in col:
                if skip_empty:
                    if v is None:
                        continue
                    if isinstance(v, str) and v.strip() == "":
                        continue
                values.append(v)
            break  # 只读取指定单列，iter_cols 这里只会有一项，读取后 break

        return values

    def create_sheet(self, sheet_name: str, index: Optional[int] = None) -> Worksheet:
        """
        在工作簿中新建一个 sheet。
        :param sheet_name: 新 sheet 名称
        :param index: 插入位置（可选），参考 openpyxl.create_sheet(index=...)
        :return: 创建或已有的 Worksheet 对象
        """
        new_ws = self.wb.create_sheet(title=sheet_name, index=index)
        return new_ws

    def write_columns(
            self,
            sheet_name: str,
            columns: Dict[Union[int, str], Iterable],
            start_row: int = 1,
            clear_first: bool = False,
            save: bool = True
    ) -> None:
        """
        将内容写到 sheet 的某些列。
        :param sheet_name: 目标 sheet 名称（若不存在则创建）
        :param columns: dict，key 为列标识（列字母或 1 起始列索引），value 为可迭代的列数据（从 start_row 开始写入）
                        例如： {"A": ["Name", "Alice"], 2: ["Age", 30]}
        :param start_row: 写入起始行（默认 1）
        :param clear_first: 是否先清除目标列区域（会按每列数据长度计算范围），默认 False
        :param save: 是否在写入后自动保存到文件（默认 True）
        """

        # 若 sheet 不存在则创建
        if sheet_name not in self.wb.sheetnames:
            ws = self.wb.create_sheet(sheet_name)
        else:
            ws = self.wb[sheet_name]

        # 将每个输入列的 iterable 转为 list（以便多次访问并获取长度）
        col_lists: Dict[int, List[Any]] = {}
        for k, iterable in columns.items():
            idx = self._col_key_to_index(k)
            # 将 iterable 转为 list（若为 generator，会被消耗后丢弃，因此强制转）
            col_lists[idx] = list(iterable)

        # 计算最大行数
        max_len = max((len(v) for v in col_lists.values()), default=0)
        if max_len == 0 and clear_first:
            # 没有数据但要求清空时不做额外动作
            max_len = 0

        # 可选：先清除旧数据（按每列 length 清除）
        if clear_first:
            for col_idx, lst in col_lists.items():
                # 清除从 start_row 到 start_row + max_len - 1
                for r in range(start_row, start_row + max_len):
                    ws.cell(row=r, column=col_idx).value = None

        # 写入数据
        for col_idx, lst in col_lists.items():
            for i, val in enumerate(lst):
                row = start_row + i
                ws.cell(row=row, column=col_idx).value = val

        # 若保存到文件
        if save:
            self.wb.save(self.filepath)

    @staticmethod
    def _col_key_to_index(col_key: Union[int, str]) -> int:
        """将列标识（字母或 1 起始索引）转换为 1 起始的整数列索引。"""
        if isinstance(col_key, int):
            if col_key < 1:
                raise ValueError("列索引应为从 1 开始的正整数")
            return col_key
        elif isinstance(col_key, str):
            try:
                return column_index_from_string(col_key)
            except Exception:
                raise ValueError(f"无效的列字母: {col_key}")
        else:
            raise TypeError("列标识必须为列字母 (str) 或 1 起始的列索引 (int)")

    def _open_workbook(self):
        try:
            self.wb = load_workbook(self.filepath, read_only=self.read_only)
        except FileNotFoundError:
            print(f'文件未找到，请配置待翻译文件！')
            raise
        except Exception as e:
            print(f'读取文件失败，发生错误: {e}')
            raise

    # 简单析构保证关闭文件句柄
    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def __enter__(self):
        if self.wb is None:
            self._open_workbook()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
