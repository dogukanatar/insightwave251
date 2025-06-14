import logging
import re
import json
import time
import os
import requests
from urllib.parse import quote_plus
import resend
from pathlib import Path
from flask import current_app, url_for
from jinja2 import Template
from openai import OpenAI
from .database import get_db_connection, get_recent_papers, get_subscribed_users
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger('INSTWAVE')

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,20}$'


class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, name, email, password_hash, language, notification_method 
                FROM users 
                WHERE email = %s
            """, (email,))
            user = cur.fetchone()
            if user and check_password_hash(user[3], password):
                return {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'language': user[4],
                    'notification_method': user[5]
                }
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
        finally:
            cur.close()
            conn.close()


class ContentService:
    @staticmethod
    def generate_email_content(papers, user):
        from .core_services import TranslationService, get_translation
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
            summary = ai_data.get('summary', '')
            evaluation = ai_data.get('evaluation', '')
            category = ai_data.get('category', '')

            if user['language'] == 'ko':
                summary = TranslationService.translate_text(summary, 'English', 'Korean')
                evaluation = TranslationService.translate_text(evaluation, 'English', 'Korean')
                category = TranslationService.translate_text(category, 'English', 'Korean')

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


class TranslationService:
    @staticmethod
    def translate_text(text, source_lang, target_lang):
        if not text: return text
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Translate from {source_lang} to {target_lang}."},
                    {"role": "user", "content": text}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text


class EmailService:
    @staticmethod
    def send_research_digest(user, content):
        try:
            subject = get_translation('email_subject', user['language'])
            template_path = Path("templates/email_base.html")
            base_template = Template(template_path.read_text())
            unsubscribe_link = url_for('api_dashboard', _external=True)

            final_html = base_template.render(
                content=content,
                unsubscribe_link=unsubscribe_link,
                user_name=user['name'],
                _=lambda key: get_translation(key, user['language'])
            )

            resend.api_key = current_app.config['RESEND_API_KEY']
            response = resend.Emails.send({
                "from": "INSTWAVE Digest <onboarding@resend.dev>",
                "to": user['email'],
                "subject": subject,
                "html": final_html
            })

            return 'id' in response
        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            return False


class KakaoService:
    CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")

    @classmethod
    def generate_auth_url(cls, user_id):
        base_url = "https://kauth.kakao.com/oauth/authorize"
        redirect_uri = url_for('kakao_callback', _external=True).replace("127.0.0.1", "localhost")
        if "localhost" in redirect_uri:
            redirect_uri = redirect_uri.replace("https://", "http://")
        params = {
            "client_id": cls.CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "talk_message",
            "state": f"{user_id}|{int(time.time())}"
        }
        return f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    @classmethod
    def handle_authorization(cls, code, state):
        try:
            user_id, _ = state.split("|", 1)
            redirect_uri = url_for('kakao_callback', _external=True).replace("127.0.0.1", "localhost")
            if "localhost" in redirect_uri:
                redirect_uri = redirect_uri.replace("https://", "http://")

            token_data = {
                "grant_type": "authorization_code",
                "client_id": cls.CLIENT_ID,
                "redirect_uri": redirect_uri,
                "code": code
            }

            response = requests.post("https://kauth.kakao.com/oauth/token", data=token_data, timeout=10)
            response.raise_for_status()
            token_info = response.json()

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM kakao_tokens WHERE user_id = %s", (user_id,))

            if cur.fetchone():
                cur.execute("""
                    UPDATE kakao_tokens 
                    SET access_token = %s, refresh_token = %s, expires_at = %s
                    WHERE user_id = %s
                """, (
                    token_info["access_token"],
                    token_info.get("refresh_token", ""),
                    time.time() + token_info["expires_in"],
                    user_id
                ))
            else:
                cur.execute("""
                    INSERT INTO kakao_tokens (user_id, access_token, refresh_token, expires_at)
                    VALUES (%s, %s, %s, %s)
                """, (
                    user_id,
                    token_info["access_token"],
                    token_info.get("refresh_token", ""),
                    time.time() + token_info["expires_in"]
                ))

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Authorization failed: {str(e)}")
            return False

    @classmethod
    def send_research_digest(cls, user, content):
        from .core_services import TranslationService
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT access_token, refresh_token, expires_at FROM kakao_tokens WHERE user_id = %s",
                        (user['id'],))
            token_data = cur.fetchone()

            if not token_data:
                return False

            access_token, refresh_token, expires_at = token_data
            if time.time() > expires_at - 300:
                if not cls._refresh_token(user['id'], refresh_token):
                    return False
                cur.execute("SELECT access_token FROM kakao_tokens WHERE user_id = %s", (user['id'],))
                access_token = cur.fetchone()[0]

            papers = get_recent_papers()
            user_topic_ids = set(user['topics'])
            user_papers = [p for p in papers if set(p['topics']) & user_topic_ids]

            if not user_papers:
                message = "📚 There are no new research papers this week."
                if user['language'] == 'ko':
                    message = "📚 이번 주에는 새로운 연구 논문이 없습니다."
            else:
                sorted_papers = sorted(user_papers, key=lambda x: x['ai_summary'].get('importance', 0), reverse=True)[
                                :2]

                message = "📚 This week's top research updates:\n\n"
                if user['language'] == 'ko':
                    message = "📚 이번 주 주요 연구 업데이트:\n\n"

                for i, paper in enumerate(sorted_papers, 1):
                    title = paper['title']
                    summary = paper['ai_summary'].get('summary', '')

                    if user['language'] == 'ko':
                        title = TranslationService.translate_text(title, 'English', 'Korean')
                        if summary:
                            summary = TranslationService.translate_text(summary, 'English', 'Korean')

                    if summary:
                        summary = summary[:100] + '...' if len(summary) > 100 else summary

                    if user['language'] == 'ko':
                        message += f"{i}. {title}\n- 요약: {summary}\n\n"
                    else:
                        message += f"{i}. {title}\n- Summary: {summary}\n\n"

            dashboard_link = url_for('api_dashboard', _external=True)
            if user['language'] == 'ko':
                message += f"\n더 많은 연구 보기: {dashboard_link}"
            else:
                message += f"\nView more research: {dashboard_link}"

            response = requests.post(
                "https://kapi.kakao.com/v2/api/talk/memo/default/send",
                headers={"Authorization": f"Bearer {access_token}"},
                data={"template_object": json.dumps({
                    "object_type": "text",
                    "text": message,
                    "link": {"web_url": dashboard_link}
                }, ensure_ascii=False)}
            )

            return response.status_code == 200 and response.json().get("result_code") == 0
        except Exception as e:
            logger.error(f"Failed to send Kakao message: {str(e)}")
            return False

    @classmethod
    def _refresh_token(cls, user_id, refresh_token):
        try:
            response = requests.post(
                "https://kauth.kakao.com/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": cls.CLIENT_ID,
                    "refresh_token": refresh_token
                },
                timeout=10
            )
            response.raise_for_status()
            new_token = response.json()

            conn = get_db_connection()
            cur = conn.cursor()
            update_params = [new_token["access_token"], time.time() + new_token["expires_in"], user_id]

            if "refresh_token" in new_token:
                cur.execute("""
                    UPDATE kakao_tokens 
                    SET access_token = %s, refresh_token = %s, expires_at = %s
                    WHERE user_id = %s
                """, (new_token["access_token"], new_token["refresh_token"], update_params[1], user_id))
            else:
                cur.execute("""
                    UPDATE kakao_tokens 
                    SET access_token = %s, expires_at = %s
                    WHERE user_id = %s
                """, update_params)

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return False


class AISummaryService:
    @staticmethod
    def generate_ai_summaries():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, arxiv_id, summary FROM thesis WHERE ai_summary IS NULL")
        rows = cur.fetchall()
        total = len(rows)
        success_count = 0
        error_count = 0

        for idx, (thesis_id, arxiv_id, summary) in enumerate(rows):
            if not summary or not arxiv_id:
                continue
            llm_json_text = AISummaryService.ask_openai(summary)
            if not llm_json_text:
                error_count += 1
                continue
            try:
                llm_json_text = re.sub(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', llm_json_text)
                llm_data = json.loads(llm_json_text)
                llm_json_string = json.dumps(llm_data, ensure_ascii=False)
                cur.execute("""
                    UPDATE thesis
                    SET ai_summary = %s,
                        updated_at = %s
                    WHERE id = %s
                """, (llm_json_string, datetime.now(), thesis_id))
                conn.commit()
                success_count += 1
            except json.JSONDecodeError as jde:
                logger.error(f"JSON Parsing Error for ID {thesis_id}: {jde}")
                error_count += 1
            except Exception as e:
                logger.error(f"Unexpected error for ID {thesis_id}: {str(e)}")
                error_count += 1

        cur.close()
        conn.close()
        logger.info(f"AI summary generation completed. Success: {success_count}, Errors: {error_count}, Total: {total}")

    @staticmethod
    def ask_openai(summary):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = f"Analyze research paper: {summary}\n- Paper summary (one line):\n- Key topics:\n- Important keywords (3-5):\n- Classification category:\n- AI evaluation:\n- Importance score (0-1):\n\nReturn JSON: {{ 'summary': '...', 'evaluation': '...', 'importance': 0.xx, 'keywords': ['...'], 'category': '...' }}"
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Expert research summarizer. Return only valid JSON."},
                          {"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None


def get_translation(key, lang='en'):
    translations = {
        'en': {
            'email_subject': 'INSTWAVE Research Digest',
            'email_greeting': 'Hello',
            'email_intro': 'Here are your personalized research updates:',
            'email_no_papers': 'There are no new papers in your topics this week',
            'category': 'Category',
            'authors': 'Authors',
            'published': 'Published',
            'summary': 'Summary',
            'ai_evaluation': 'AI Evaluation',
            'view_full_paper': 'View Full Paper'
        },
        'ko': {
            'email_subject': 'INSTWAVE 연구 요약 리포트',
            'email_greeting': '안녕하세요',
            'email_intro': '개인 맞춤 연구 업데이트를 확인해 보세요:',
            'email_no_papers': '이번 주에는 새로운 논문이 없습니다',
            'category': '분류',
            'authors': '저자',
            'published': '게시일',
            'summary': '요약',
            'ai_evaluation': 'AI 평가',
            'view_full_paper': '전체 논문 보기'
        }
    }
    return translations.get(lang, {}).get(key, key)
