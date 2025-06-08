def merge_weekly_arxiv_from_firestore_by_published(request):
    from google.cloud import storage, firestore
    from datetime import datetime, timedelta
    import pytz, json
    
    # Get today's date in UTC
    today_utc = datetime.utcnow().date()

    # Calculate last week's Monday and this week's Monday (UTC)
    last_monday = today_utc - timedelta(days=today_utc.weekday() + 7)
    this_monday = last_monday + timedelta(days=7)

    # Set published date range in ISO 8601 string format (UTC)
    start_published = f"{last_monday}T00:00:00Z"
    end_published = f"{this_monday}T00:00:00Z"

    # Initialize Firestore client
    db = firestore.Client()

    # Initialize Google Cloud Storage client
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('aplusbcd')

    # Query papers published within the specified date range (UTC)
    query = db.collection('arxiv_papers')\
        .where('published', '>=', start_published)\
        .where('published', '<=', end_published)

    docs = query.stream()

    merged_content = ''
    count = 0

    # Combine papers into JSON Lines format string
    for doc in docs:
        paper = doc.to_dict()
        merged_content += json.dumps(paper, ensure_ascii=False) + '\n'
        count += 1

    # Define the final file name for merged JSONL file
    merged_file_name = f'crawl_data/arxiv_papers_{last_monday}_to_{this_monday}.jsonl'

    # Upload the merged content to Google Cloud Storage
    blob = bucket.blob(merged_file_name)
    blob.upload_from_string(merged_content.strip(), content_type='application/json')

    return f'✅ Merged {count} papers from Firestore (based on published date): {merged_file_name}'
