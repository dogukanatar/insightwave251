# services/content_generator.py
import logging

logger = logging.getLogger('INSTWAVE')


def generate_email_content(papers, user):
    """Generate personalized email content with limit of 3 papers"""
    try:
        user_topic_ids = set(user['topics'])
        user_papers = [
            p for p in papers
            if set(p['topics']) & user_topic_ids
        ]

        if not user_papers:
            return f"""
            <div class="no-papers">
                <h3>Hello {user['name']},</h3>
                <p>There are no new papers in your topics this week.</p>
                <p>Check back next Tuesday for new research updates!</p>
            </div>
            """

        # 按重要性排序，取最重要的3篇论文
        sorted_papers = sorted(
            user_papers,
            key=lambda x: x['ai_summary'].get('importance', 0),
            reverse=True
        )[:3]

        paper_items = []
        for i, p in enumerate(sorted_papers, 1):
            # 提取AI摘要数据
            ai_data = p['ai_summary']
            category = ai_data.get('category', 'General')
            importance = ai_data.get('importance', 0.8)
            summary = ai_data.get('summary', '')
            keywords = ai_data.get('keywords', [])

            # 评估标签（基于重要性）
            if importance > 0.9:
                importance_label = "🌟 Highly Recommended"
            elif importance > 0.7:
                importance_label = "👍 Recommended"
            else:
                importance_label = "📖 Worth Reading"

            paper_items.append(f"""
            <div class="paper">
                <div class="paper-number">{i}</div>
                <h3 class="paper-title">{p['title']}</h3>
                <div class="paper-header">
                    <span class="paper-category">{category}</span>
                    <span class="paper-importance">{importance_label}</span>
                </div>
                <div class="paper-meta">
                    <div class="paper-authors"><strong>Authors:</strong> {p['author']}</div>
                    <div class="paper-date"><strong>Published:</strong> {p['date']}</div>
                </div>
                <div class="paper-summary">
                    <p>{summary[:200]}{'...' if len(summary) > 200 else ''}</p>
                </div>
                {f'<div class="paper-keywords"><strong>Keywords:</strong> {", ".join(keywords[:3])}</div>' if keywords else ''}
                <a href="{p['link']}" class="paper-link">View Full Paper &rarr;</a>
            </div>
            """)

        paper_items_html = "\n".join(paper_items)

        # 添加剩余论文提示
        additional_count = len(user_papers) - len(sorted_papers)
        more_papers_html = ""
        if additional_count > 0:
            more_papers_html = f"""
            <div class="more-papers">
                View {additional_count} additional papers in your dashboard
                <br>
                <a href="https://yourdomain.com/dashboard" class="more-link">Go to Dashboard</a>
            </div>
            """

        return paper_items_html + more_papers_html
    except Exception as e:
        logger.error(f"Error generating email content: {str(e)}")
        return """
        <div class="error">
            <h3>Content Generation Error</h3>
            <p>We encountered an issue preparing your research digest.</p>
            <p>Our team has been notified and is working to resolve the issue.</p>
        </div>
        """
