"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface LanguageContextType {
  lang: string;
  setLang: (lang: string) => void;
  t: (key: string) => string;
}

interface Translations {
  [lang: string]: {
    [key: string]: string;
  };
}

const translations: Translations = {
  en: {
    login_title: "INSTWAVE Research Digest",
    login_email: "Email",
    login_password: "Password",
    login_button: "Login",
    login_signup: "New user? Create account",
    register_title: "Create INSTWAVE Account",
    register_name: "Full Name",
    register_email: "Email Address",
    register_password: "Password",
    register_button: "Register",
    register_login: "Already have an account? Login here",
    password_requirements: "8-20 characters with letters and numbers",
    dashboard_title: "Your Preferences",
    notification_settings: "Notification Settings",
    preferred_language: "Preferred Language",
    english: "English",
    korean: "Korean",
    notification_method: "Notification Method",
    email_only: "Email Only",
    kakao_only: "Kakao Only",
    both: "Email & Kakao",
    kakao_account: "Kakao Account",
    connected: "Connected",
    not_connected: "Not Connected",
    connect_kakao: "Connect Kakao Account",
    receive_notifications: "Receive weekly notifications",
    research_topics: "Research Topics",
    save_preferences: "Save Preferences",
    subscription_details: "Subscription Details",
    next_digest: "Next Digest",
    status: "Status",
    active: "Active",
    inactive: "Inactive",
    send_now: "Send Weekly Digest Now",
    send_note: "Receive this week's research updates immediately",
    topic_selection_note: "Select research topics you're interested in",
    kakao_note: "After connecting, you will receive notifications via Kakao but without alerts",
    logout: "Logout",
    language: "Language",
    logging_in: "Logging in...",
    registering: "Registering...",
    saving: "Saving...",
    sending: "Sending...",
    select_language: "Select language",
    authors: "Authors",
    published: "Published",
    summary: "Summary",
    ai_evaluation: "AI Evaluation",
    view_full_paper: "View Full Paper",
    category: "Category",
    manage_preferences: "Manage Preferences",
    unsubscribe: "Unsubscribe",
    brand_name: "INSTWAVE",
    tagline: "AI Research Paper Digest System",
    at_least_one_topic: "Please select at least 1 research topic",
    create_account: "Create account",
    login_here: "Login here",
    topics_selected: "topics selected",
    select_more: "Select",
    reconnect_kakao: "Reconnect Kakao Account",
    kakao_reconnected: "Kakao account reconnected successfully!",
  },
  ko: {
    login_title: "INSTWAVE 연구 논문 요약",
    login_email: "이메일",
    login_password: "비밀번호",
    login_button: "로그인",
    login_signup: "신규 사용자? 계정 만들기",
    register_title: "INSTWAVE 계정 만들기",
    register_name: "이름",
    register_email: "이메일 주소",
    register_password: "비밀번호",
    register_button: "등록",
    register_login: "이미 계정이 있으신가요? 로그인하기",
    password_requirements: "8-20자, 영문과 숫자 포함",
    dashboard_title: "사용자 설정",
    notification_settings: "알림 설정",
    preferred_language: "선호 언어",
    english: "영어",
    korean: "한국어",
    notification_method: "알림 방법",
    email_only: "이메일만",
    kakao_only: "카카오톡만",
    both: "이메일 및 카카오톡",
    kakao_account: "카카오 계정",
    connected: "연결됨",
    not_connected: "연결 안 됨",
    connect_kakao: "카카오 계정 연결",
    receive_notifications: "주간 알림 수신",
    research_topics: "연구 주제",
    save_preferences: "설정 저장",
    subscription_details: "구독 정보",
    next_digest: "다음 요약",
    status: "상태",
    active: "활성화",
    inactive: "비활성화",
    send_now: "지금 주간 요약 받기",
    send_note: "이번 주 연구 업데이트를 즉시 받아보세요",
    topic_selection_note: "관심 있는 연구 주제를 선택하세요",
    kakao_note: "연결 후 카카오톡으로 알림을 받게 되지만 알림음 없이 조용히 전달됩니다",
    logout: "로그아웃",
    language: "언어",
    logging_in: "로그인 중...",
    registering: "등록 중...",
    saving: "저장 중...",
    sending: "전송 중...",
    select_language: "언어 선택",
    authors: "저자",
    published: "게시일",
    summary: "요약",
    ai_evaluation: "AI 평가",
    view_full_paper: "전체 논문 보기",
    category: "분류",
    manage_preferences: "설정 관리",
    unsubscribe: "구독 취소",
    brand_name: "INSTWAVE",
    tagline: "AI 연구 논문 요약 시스템",
    at_least_one_topic: "최소 1개의 연구 주제를 선택해주세요",
    create_account: "계정 만들기",
    login_here: "로그인하기",
    topics_selected: "개 주제 선택됨",
    select_more: "선택",
    reconnect_kakao: "카카오 계정 재연결",
    kakao_reconnected: "카카오 계정이 성공적으로 재연결되었습니다!",
  }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
  const [lang, setLang] = useState('en');

  useEffect(() => {
    const savedLang = localStorage.getItem('lang');
    const browserLang = navigator.language.startsWith('ko') ? 'ko' : 'en';
    setLang(savedLang || browserLang);
  }, []);

  useEffect(() => {
    localStorage.setItem('lang', lang);
  }, [lang]);

  const t = (key: string) => {
    const langTranslations = translations[lang];
    return langTranslations?.[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
