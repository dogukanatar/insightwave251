# services/translation.py
import re
from openai import OpenAI
import os
from flask import current_app
import logging

logger = logging.getLogger('INSTWAVE')


def translate_content(content, source_lang, target_lang):
    """Translate content using OpenAI"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        if "<div" in content or "<p>" in content:
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
        return content
