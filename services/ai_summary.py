import psycopg2
from openai import OpenAI
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from .database import get_db_connection
import logging
import re

logger = logging.getLogger('INSTWAVE')

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(summary):
    """Generate summary in English only"""
    prompt = f"""
Please analyze the following research paper:

{summary}

- Paper summary (one line):
- Key topics:
- Important keywords (3-5):
- Classification category (e.g., Computer Vision, NLP):
- AI evaluation (may include subjective interpretation):
- Importance score (0-1 floating point):

Organize the results in the following JSON format:

{{
  "summary": "...",
  "evaluation": "...",
  "importance": 0.xx,
  "keywords": ["...", "...", "..."],
  "category": "..."
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert research paper summarizer. Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[OpenAI API error] {e}")
        return None

def generate_ai_summaries():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch theses without AI summaries
    cur.execute("""
        SELECT id, arxiv_id, summary FROM thesis
        WHERE ai_summary IS NULL
    """)
    rows = cur.fetchall()

    # Track progress
    total = len(rows)
    success_count = 0
    error_count = 0

    for idx, (thesis_id, arxiv_id, summary) in enumerate(rows):
        if not summary or not arxiv_id:
            continue

        logger.info(f"[Summarizing] ID: {thesis_id}, arXiv: {arxiv_id} ({idx + 1}/{total})")

        # Generate summary in English only
        llm_json_text = ask_openai(summary)
        if not llm_json_text:
            error_count += 1
            continue

        logger.debug(f"OpenAI response for ID {thesis_id}: {llm_json_text}")

        try:
            # Fix JSON escape issues
            llm_json_text = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', llm_json_text)
            llm_data = json.loads(llm_json_text)
            llm_json_string = json.dumps(llm_data, ensure_ascii=False)

            # Update database
            cur.execute("""
                UPDATE thesis
                SET ai_summary = %s,
                    updated_at = %s
                WHERE id = %s
            """, (llm_json_string, datetime.now(), thesis_id))
            conn.commit()

            success_count += 1
            logger.info(f"[Completed] ID: {thesis_id} - AI summary saved to database")

        except json.JSONDecodeError as jde:
            logger.error(f"JSON Parsing Error for ID {thesis_id}: {jde}. Response: {llm_json_text}")
            error_count += 1
        except Exception as e:
            logger.error(f"Unexpected error for ID {thesis_id}: {str(e)}")
            error_count += 1

    cur.close()
    conn.close()

    # Summary report
    logger.info(f"AI summary generation completed. "
                f"Success: {success_count}, Errors: {error_count}, Total: {total}")
