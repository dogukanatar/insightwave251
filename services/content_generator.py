import logging
from i18n import get_translation
from .translation_service import translate_text

logger = logging.getLogger('INSTWAVE')


def generate_email_content(papers, user):
    try:
        user_topic_ids = set(user['topics'])
        user_papers = [p for p in papers if set(p['topics']) & user_topic_ids]

        if not user_papers:
            return f"""
            <div class="no-papers">
                <h3>{get_translation('email_greeting', user['language'])} {user['name']},</h3>
                <p>{get_translation('email_no_papers', user['language'])}</p>
                <p>{get_translation('email_intro', user['language'])}</p>
            </div>
            """

        sorted_papers = sorted(user_papers, key=lambda x: x['ai_summary'].get('importance', 0), reverse=True)[:3]
        paper_items = []

        for i, p in enumerate(sorted_papers, 1):
            ai_data = p['ai_summary']

            summary_en = ai_data.get('summary', '')
            evaluation_en = ai_data.get('evaluation', '')
            category_en = ai_data.get('category', '')

            if user['language'] == 'ko':
                summary = translate_text(summary_en, 'English', 'Korean')
                evaluation = translate_text(evaluation_en, 'English', 'Korean')
                category = translate_text(category_en, 'English', 'Korean')
            else:
                summary = summary_en
                evaluation = evaluation_en
                category = category_en

            importance = ai_data.get('importance', 0.8)
            keywords = ai_data.get('keywords', [])

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
                    <span class="paper-category">{get_translation('category', user['language'])}: {category}</span>
                    <span class="paper-importance">{importance_label}</span>
                </div>
                <div class="paper-meta">
                    <div class="paper-authors"><strong>{get_translation('authors', user['language'])}:</strong> {p['author']}</div>
                    <div class="paper-date"><strong>{get_translation('published', user['language'])}:</strong> {p['date']}</div>
                </div>
                <div class="paper-summary">
                    <h4>{get_translation('summary', user['language'])}</h4>
                    <p>{summary}</p>
                </div>
                <div class="paper-evaluation">
                    <h4>{get_translation('ai_evaluation', user['language'])}</h4>
                    <p>{evaluation}</p>
                </div>
                <a href="{p['link']}" class="paper-link">{get_translation('view_full_paper', user['language'])} &rarr;</a>
            </div>
            """)

        return "\n".join(paper_items)

    except Exception as e:
        logger.error(f"Error generating email content: {str(e)}")
        return """
        <div class="error">
            <h3>Content Generation Error</h3>
            <p>We encountered an issue preparing your research digest.</p>
            <p>Our team has been notified and is working to resolve the issue.</p>
        </div>
        """
