class Config:
    def __init__(self):
        self.current_languages = ["英语", '汉语']  # 当前的语言
        self.target_language = "法语"  # 目标翻译为语言
        self.open_ai_base_url = "https://aihubmix.com/v1"
        self.open_ai_api_key = "sk-Re9PZYsLEPnSoNOV810e36F8F2744d1dA01aD460Cf546254"
        self.open_ai_model = "doubao-seed-code-free"  # 大模型的名称
        self.batch_size = 50  # 批量处理的数据，最多50个
        self.file_name = "Translate.xlsx"  # 待翻译的文件名称，必须放到当前项目根目录下面，用英文命令
        self.translate_sheet_name = "Sheet1"
        self.translate_model = "column"  # 翻译的方式，按照单列(column)或全文翻译(all)
        self.translate_sheet_column = "A"  # 只有单列的时候需要，指定列的名称


config = Config()
