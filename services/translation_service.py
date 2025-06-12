import os
import logging
from openai import OpenAI

logger = logging.getLogger('INSTWAVE')


def translate_text(text, source_lang, target_lang):
    """Translate text using OpenAI"""
    if not text:
        return text

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following text from {source_lang} to {target_lang}."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text
