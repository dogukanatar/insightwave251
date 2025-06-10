import os
import json
import psycopg2
from google.cloud import storage
from datetime import datetime, timedelta

def fetch_and_store(request):
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")

    bucket_name = "aplusbcd"
    folder_path = "crawl_data"

    today = datetime.utcnow()
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(days=7)

    start_date_str = last_monday.strftime("%Y-%m-%d")
    end_date_str = this_monday.strftime("%Y-%m-%d")

    file_name = f"{folder_path}/arxiv_papers_{start_date_str}_to_{end_date_str}.jsonl"

    print(f"처리할 파일명: {file_name}")

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    if not blob.exists():
        print(f"파일 {file_name} 이 존재하지 않습니다.")
        return "파일 없음"

    content = blob.download_as_text()

    conn = psycopg2.connect(
        host='10.73.208.3', 
        dbname=db_name,
        user=db_user,
        password=db_password
    )

    cursor = conn.cursor()

    for line in content.strip().split("\n"):
        data = json.loads(line)

        title = data.get("title")
        authors = ", ".join(data.get("authors", []))
        summary = data.get("summary")
        arxiv_id = data.get("arxiv_id")
        publish_date = data.get("published", "")[:10]  
        categories = data.get("categories", [])

        cursor.execute(
            """
            INSERT INTO thesis (title, author, summary, arxiv_id, publish_date, categories)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (arxiv_id) DO NOTHING
            """,
            (title, authors, summary, arxiv_id, publish_date, categories)
        )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"{file_name} 의 데이터를 성공적으로 DB에 저장했습니다.")
    return "완료"


