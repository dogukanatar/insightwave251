import psycopg2
from openai import OpenAI
import json
from datetime import datetime
from google.cloud import storage
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로딩
load_dotenv()

# GCP 서비스 계정 인증
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# GCP 정보 설정
BUCKET_NAME = os.getenv("BUCKET_NAME")

# OpenAI API
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
                {"role": "system", "content": "너는 논문 요약 전문가야. 명확한 JSON 응답만 반환해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[OpenAI API 오류] {e}")
        return None

# GCS 업로드 함수
def upload_to_gcs(bucket_name, source_file, destination_blob):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(source_file)
    print(f"✅ GCS 업로드 완료: gs://{bucket_name}/{destination_blob}")

# DB 연결
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# 요약할 논문 조회
cur.execute("""
    SELECT id, arxiv_id, summary FROM Thesis
    WHERE ai_summary IS NULL
""")
rows = cur.fetchall()

for thesis_id, arxiv_id, summary in rows:
    if not summary or not arxiv_id:
        continue

    print(f"\n[요약 중] ID: {thesis_id}, arXiv: {arxiv_id}")
    llm_json_text = ask_openai(summary)
    if not llm_json_text:
        continue

    try:
        llm_data = json.loads(llm_json_text)
        llm_json_string = json.dumps(llm_data, ensure_ascii=False)

        # DB 업데이트
        cur.execute("""
            UPDATE Thesis
            SET ai_summary = %s,
                updated_at = %s
            WHERE id = %s
        """, (llm_json_string, datetime.now(), thesis_id))
        conn.commit()

        # 파일 저장 및 업로드
        filename = f"{arxiv_id}_analysis.json"
        local_path = os.path.join("llm_summarized", filename)
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump({
                "id": thesis_id,
                "arxiv_id": arxiv_id,
                "ai_summary": llm_data
            }, f, ensure_ascii=False, indent=2)

        gcs_path = f"llm_summerized/{filename}"
        upload_to_gcs(BUCKET_NAME, local_path, gcs_path)

        print(f"[완료] ID: {thesis_id}, 파일명: {filename}")

    except json.JSONDecodeError:
        print(f"[JSON 파싱 오류] ID: {thesis_id}")
        continue

# 마무리
cur.close()
conn.close()
