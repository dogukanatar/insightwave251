import psycopg2
from openai import OpenAI
import json
from datetime import datetime
# from google.cloud import storage
import os
from dotenv import load_dotenv
from .database import get_db_connection
from flask import current_app
import logging

logger = logging.getLogger('INSTWAVE')

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(summary, model="gpt-3.5-turbo"):
    prompt = f"""
다음 논문 원문을 분석해줘:

{summary}

- 논문 요약 (한 줄):
- 핵심 주제:
- 중요 키워드 3~5개:
- 분류 카테고리 (ex: Computer Vision, NLP 등):
- AI 평가 (주관적인 해석 포함 가능):
- 중요도 점수 (0~1 부동소수점 수치):

결과를 다음 JSON 포맷으로 정리해줘:

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
            model=model,
            messages=[
                {"role": "system", "content": "너는 논문 요약 전문가야. 결과는 오직 명확한 JSON 형태로만 반환해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[OpenAI API 오류] {e}")
        return None

# def upload_to_gcs(bucket_name, source_file, destination_blob):
#     try:
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(bucket_name)
#         blob = bucket.blob(destination_blob)
#         blob.upload_from_filename(source_file)
#         logger.info(f"✅ GCS 업로드 완료: gs://{bucket_name}/{destination_blob}")
#         return True
#     except Exception as e:
#         logger.error(f"GCS 업로드 오류: {e}")
#         return False

def generate_ai_summaries():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch theses without AI summaries
    cur.execute("""
        SELECT id, arxiv_id, summary FROM thesis
        WHERE ai_summary IS NULL
    """)
    rows = cur.fetchall()

    for thesis_id, arxiv_id, summary in rows:
        if not summary or not arxiv_id:
            continue

        logger.info(f"[Summarizing] ID: {thesis_id}, arXiv: {arxiv_id}")
        llm_json_text = ask_openai(summary)
        if not llm_json_text:
            continue

        logger.debug(f"OpenAI response for ID {thesis_id}: {llm_json_text}")

        try:
            # 修复JSON转义问题
            llm_json_text = llm_json_text.replace('\\$', '$')
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

            # filename = f"{arxiv_id}_analysis.json"
            # local_path = os.path.join("llm_summarized", filename)
            #
            # with open(local_path, "w", encoding="utf-8") as f:
            #     json.dump({
            #         "id": thesis_id,
            #         "arxiv_id": arxiv_id,
            #         "ai_summary": llm_data
            #     }, f, ensure_ascii=False, indent=2)
            #
            # gcs_path = f"llm_summerized/{filename}"
            #
            # if not upload_to_gcs(current_app.config['BUCKET_NAME'], local_path, gcs_path):
            #     logger.error(f"Failed to upload {local_path} to GCS.")
            #     continue

            logger.info(f"[Completed] ID: {thesis_id} - AI summary saved to database")

        except json.JSONDecodeError as jde:
            logger.error(f"JSON Parsing Error for ID {thesis_id}: {jde}. Response: {llm_json_text}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error for ID {thesis_id}: {str(e)}")
            continue

    cur.close()
    conn.close()
    logger.info("AI summary generation completed. All results saved to database.")
