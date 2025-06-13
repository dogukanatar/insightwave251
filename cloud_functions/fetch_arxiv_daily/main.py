def fetch_arxiv_daily(request):
    try:
        import requests, feedparser, json
        from datetime import datetime, timedelta, timezone
        from pathlib import Path
        import pytz
        from google.cloud import storage, firestore
        import time
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        today = datetime.now(timezone.utc).date()
        crawl_date = today - timedelta(days=1)

        keywords_by_discipline = {
            'Computer Science': [
                'artificial intelligence', 'machine learning', 'deep learning', 'reinforcement learning',
                'robotics', 'self-driving', 'large language model', 'natural language processing',
                'computer vision', 'data mining', 'big data', 'explainable AI', 'federated learning',
                'edge computing', 'blockchain', 'security', 'quantum computing', 'knowledge graph',
                'recommender system', 'graph neural network'
            ],
            'Economics': [
                'economics', 'public policy', 'financial modeling', 'algorithmic trading',
                'development studies', 'behavioral economics', 'game theory', 'market design',
                'environmental economics', 'health economics', 'labor economics', 'risk management',
                'macroeconomics', 'microeconomics', 'international trade'
            ],
            'Electrical Engineering and Systems Science': [
                'signal processing', 'control systems', 'embedded systems', 'wireless communication',
                'information theory', 'circuit design', 'semiconductor', 'power systems', 'smart grid',
                'electromagnetic field', 'sensor networks', 'autonomous systems', 'cyber-physical systems',
                'renewable energy', 'energy harvesting', 'vehicular networks', 'AIoT', '5G', 'low-power design'
            ],
            'Mathematics': [
                'numerical analysis', 'optimization', 'cryptography', 'graph theory', 'algebra',
                'topology', 'geometry', 'probability', 'statistics', 'combinatorics',
                'differential equations', 'functional analysis', 'discrete mathematics',
                'mathematical modeling', 'stochastic processes'
            ],
            'Physics': [
                'astrophysics', 'cosmology', 'plasma physics', 'gravitational wave', 'dark matter',
                'nuclear physics', 'condensed matter', 'nanomaterials', 'materials science',
                'quantum computing', 'meteorology', 'geophysics', 'climate change', 'energy systems',
                'superconductivity', 'electron dynamics', 'statistical mechanics', 'exoplanet studies'
            ],
            'Quantitative Biology': [
                'bioinformatics', 'genomics', 'proteomics', 'metabolomics', 'gene therapy',
                'epidemiology', 'systems biology', 'computational biology', 'single-cell analysis',
                'CRISPR', 'population genetics', 'computational neuroscience', 'molecular dynamics',
                'synthetic biology', 'cancer genomics'
            ],
            'Quantitative Finance': [
                'financial modeling', 'algorithmic trading', 'risk management', 'quantitative analysis',
                'time series analysis', 'stochastic modeling', 'derivatives pricing',
                'portfolio optimization', 'market microstructure', 'volatility modeling',
                'option pricing', 'asset pricing', 'high-frequency trading'
            ],
            'Statistics': [
                'data mining', 'big data', 'supervised learning', 'unsupervised learning',
                'anomaly detection', 'time series analysis', 'probability theory', 'statistical inference',
                'causal inference', 'Bayesian statistics', 'Monte Carlo simulation',
                'hierarchical modeling', 'survival analysis', 'regression analysis'
            ]
        }
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(['GET', 'POST'])
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)


        def fetch_arxiv_papers(keyword, start=0, max_results=100):
            base_url = 'http://export.arxiv.org/api/query?'
            query = f'all:{keyword}'
            url = f'{base_url}search_query={query}&start={start}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'
            headers = {
             'User-Agent': 'MyArxivCrawler/1.0 (https://github.com/INSTWAVE-A-BCD/INSTWAVE; contact: aplusbcd1@gmail.com)'
            }

            try:
                response = session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f'❌ Error fetching {url}: {e}')
                return []
            feed = feedparser.parse(response.text)
            return feed.entries

        papers_by_id = {}
        for discipline, keywords in keywords_by_discipline.items():
            for keyword in keywords:
                start, max_results_per_call, should_stop = 0, 100, False
                while not should_stop:
                    entries = fetch_arxiv_papers(keyword, start, max_results_per_call)
                    if not entries:
                        break
                    for entry in entries:
                        published_str = getattr(entry, 'published', None)
                        if not published_str:
                            continue
                        published_dt = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                        published_date = published_dt.date()
                        if published_date != crawl_date:
                            if published_date < crawl_date:
                                should_stop = True
                            continue
                        arxiv_id = entry.id.split('/abs/')[-1]
                        if arxiv_id not in papers_by_id:
                            papers_by_id[arxiv_id] = {
                                'arxiv_id': arxiv_id,
                                'title': entry.title.strip().replace('\n', ' '),
                                'summary': entry.summary.strip().replace('\n', ' '),
                                'authors': [author.name for author in entry.authors],
                                'published': published_str,
                                'categories': [tag['term'] for tag in getattr(entry, 'tags', [])],
                                'link_abstract': entry.link,
                                'link_pdf': '',
                                'crawl_date': today.strftime('%Y-%m-%d'),
                                'keywords': set(),
                                'disciplines': set()
                            }
                            for link in entry.links:
                                if link.rel == 'related' and 'pdf' in link.href:
                                    papers_by_id[arxiv_id]['link_pdf'] = link.href
                        papers_by_id[arxiv_id]['keywords'].add(keyword)
                        papers_by_id[arxiv_id]['disciplines'].add(discipline)
                    if should_stop:
                        break
                    start += max_results_per_call
                    time.sleep(3)

        for paper in papers_by_id.values():
            paper['keywords'] = list(paper['keywords'])
            paper['disciplines'] = list(paper['disciplines'])

        db = firestore.Client()
        for arxiv_id, paper in papers_by_id.items():
            doc_ref = db.collection('arxiv_papers').document(arxiv_id)
            doc_ref.set(paper)

        return '✅ Papers fetched and saved!'

    except Exception as e:
        import traceback
        print('❌ Exception occurred:', e)
        print(traceback.format_exc())
        return '❌ Error occurred during fetching'
