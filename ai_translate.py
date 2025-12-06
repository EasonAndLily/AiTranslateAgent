from config import Config
from openai import OpenAI


class AiTranslate:
    def __init__(self, config: Config, texts: list):
        self.texts = texts
        self.config = config
        self.client = OpenAI(api_key=self.config.open_ai_api_key, base_url=self.config.open_ai_base_url)

    def translate_to(self):
        if not self.texts:
            return []

        # 过滤空文本
        valid_texts = [text for text in self.texts if text and text.strip()]
        if not valid_texts:
            return [(text, '') for text in self.texts]

        # 批量翻译
        translated_results = self._call_translate_api(valid_texts)

        # 解析结果并构建返回列表
        return self._parse_translation_results(translated_results)

    def _call_translate_api(self, texts):

        """批量调用OpenAI翻译API"""
        try:
            # 构建批量翻译的提示词
            text_list = '\n'.join([f"{i + 1}. {text}" for i, text in enumerate(texts)])
            prompt = f'''你是一个专业的翻译助手。当前待翻译的文本可能包含多种语言：{self.config.current_languages}，请将文本批量翻译成{self.config.target_language}。
                要求：
                1. 对于每个文本，返回格式为："原始文本 -> 翻译结果"
                2. 每个翻译结果占一行
                3. 只返回翻译结果，不要添加任何解释
                4. 保持原始文本的顺序
                5. 遇到无法翻译的字符、文本等，返回原始文本
    
                需要翻译的文本：
                {text_list}'''
            messages = [
                {
                    'role': 'system',
                    'content': '专业翻译助手，严格返回要求格式'
                },
                {
                    'role': 'user',
                    'content': prompt
                }

            ]
            res = self.client.chat.completions.create(model=self.config.open_ai_model, messages=messages,
                                                      temperature=0.1)

            return res.choices[0].message.content.strip()

        except Exception as e:
            print(f"翻译错误: {e}")
            # 错误时返回原始文本列表
            return '\n'.join([f"{text} -> {text}" for text in texts])

    def _parse_translation_results(self, result_text):
        """解析批量翻译结果"""
        translated_pairs = []

        # 按行分割结果
        lines = result_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if ' -> ' in line:
                # 解析格式："原始文本 -> 翻译结果"
                parts = line.split(' -> ', 1)
                if len(parts) == 2:
                    translated = parts[1].strip()
                    translated_pairs.append(translated)

        return translated_pairs


# 示例用法
def main():
    # 示例：将英文翻译为法文
    texts = ["Hello world", "Thank you", "How are you?"]
    config = Config()
    # 创建翻译器实例
    translate = AiTranslate(config, texts)

    # 批量翻译为目标语言
    results = translate.translate_to()
    # 打印结果
    print(f"翻译结果: {results}")


if __name__ == "__main__":
    main()
