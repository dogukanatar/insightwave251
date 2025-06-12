import os
import json
import time
import logging
import requests
from urllib.parse import quote_plus
from flask import current_app, url_for
from .database import get_db_connection, get_recent_papers
from .translation_service import translate_text

logger = logging.getLogger('INSTWAVE')


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
            if "|" not in state:
                raise ValueError("Invalid state parameter")
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
            required_keys = {"access_token", "token_type", "expires_in"}
            if not required_keys.issubset(token_info.keys()):
                raise ValueError("Invalid token response")
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM kakao_tokens WHERE user_id = %s", (user_id,))
            if cur.fetchone():
                cur.execute("""
                    UPDATE kakao_tokens 
                    SET access_token = %s, refresh_token = %s, expires_at = %s
                    WHERE user_id = %s
                """, (
                token_info["access_token"], token_info.get("refresh_token", ""), time.time() + token_info["expires_in"],
                user_id))
            else:
                cur.execute("""
                    INSERT INTO kakao_tokens (user_id, access_token, refresh_token, expires_at)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, token_info["access_token"], token_info.get("refresh_token", ""),
                      time.time() + token_info["expires_in"]))
            conn.commit()
            logger.info(f"User {user_id} Kakao authorization successful")
            return True
        except Exception as e:
            logger.error(f"Authorization failed: {str(e)}")
            return False

    @classmethod
    def send_research_digest(cls, user, content):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                    SELECT access_token, refresh_token, expires_at 
                    FROM kakao_tokens 
                    WHERE user_id = %s
                """, (user['id'],))
            token_data = cur.fetchone()
            if not token_data:
                logger.warning(f"No Kakao token for user {user['id']}")
                return False
            access_token, refresh_token, expires_at = token_data
            if time.time() > expires_at - 300:
                if not cls._refresh_token(user['id'], refresh_token):
                    return False
                cur.execute("""
                        SELECT access_token 
                        FROM kakao_tokens 
                        WHERE user_id = %s
                    """, (user['id'],))
                access_token = cur.fetchone()[0]

            papers = get_recent_papers()
            user_topic_ids = set(user['topics'])
            user_papers = [p for p in papers if set(p['topics']) & user_topic_ids]

            if not user_papers:
                if user['language'] == 'ko':
                    message = "📚 이번 주에는 새로운 연구 논문이 없습니다."
                else:
                    message = "📚 There are no new research papers this week."
            else:
                sorted_papers = sorted(
                    user_papers,
                    key=lambda x: x['ai_summary'].get('importance', 0),
                    reverse=True
                )[:2]

                if user['language'] == 'ko':
                    message = "📚 이번 주 주요 연구 업데이트:\n\n"
                    for i, paper in enumerate(sorted_papers, 1):
                        title = translate_text(paper['title'], 'English', 'Korean')
                        summary = paper['ai_summary'].get('summary', '')
                        if summary:
                            summary = translate_text(summary, 'English', 'Korean')
                            summary = summary[:100] + '...' if len(summary) > 100 else summary
                        message += f"{i}. {title}\n- 요약: {summary}\n\n"
                else:
                    message = "📚 This week's top research updates:\n\n"
                    for i, paper in enumerate(sorted_papers, 1):
                        title = paper['title']
                        summary = paper['ai_summary'].get('summary', '')
                        if summary:
                            summary = summary[:100] + '...' if len(summary) > 100 else summary
                        message += f"{i}. {title}\n- Summary: {summary}\n\n"

            dashboard_link = url_for('dashboard', _external=True)
            if user['language'] == 'ko':
                message += f"\n더 많은 연구 보기: {dashboard_link}"
            else:
                message += f"\nView more research: {dashboard_link}"

            response = requests.post(
                "https://kapi.kakao.com/v2/api/talk/memo/default/send",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
                },
                data={
                    "template_object": json.dumps({
                        "object_type": "text",
                        "text": message,
                        "link": {
                            "web_url": dashboard_link,
                            "mobile_web_url": dashboard_link
                        }
                    }, ensure_ascii=False)
                },
                timeout=10
            )

            if response.status_code == 200 and response.json().get("result_code") == 0:
                logger.info(f"Kakao message sent to user {user['id']}")
                return True
            else:
                logger.error(f"Kakao API error: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Failed to send Kakao message: {str(e)}")
            return False

    @classmethod
    def _refresh_token(cls, user_id, refresh_token):
        try:
            if not refresh_token:
                logger.error(f"No refresh token for user {user_id}")
                return False
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
            logger.info(f"Refreshed Kakao token for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return False
