# services/translation.py
import re  # 添加re模块导入
from openai import OpenAI
import os
from flask import current_app
import logging

logger = logging.getLogger('INSTWAVE')


def translate_content(content, source_lang, target_lang):
    """Translate content using OpenAI"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 添加对HTML内容的特殊处理
        if "<div" in content or "<p>" in content:
            # 提取文本内容进行翻译
            text_content = re.sub(r'<[^>]+>', '', content)
            translated = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following content from {source_lang} to {target_lang}."
                    },
                    {
                        "role": "user",
                        "content": text_content
                    }
                ],
                temperature=0.1
            )
            translated_text = translated.choices[0].message.content.strip()
            return content.replace(text_content, translated_text)
        else:
            # 普通文本翻译
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the following content from {source_lang} to {target_lang}."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return content  # 失败时返回原始内容
