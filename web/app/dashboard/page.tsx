"use client"
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useRouter } from "next/navigation";
import { getDashboardData, updatePreferences, sendWeeklyDigestNow, getKakaoAuthUrl } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface Topic {
  id: number;
  label: string;
}

interface DashboardData {
  id: number;
  name: string;
  email: string;
  language: string;
  notification_method: string;
  active: boolean;
  user_topics: number[];
  all_topics: Topic[];
  next_tuesday: string;
  kakao_connected: boolean;
}

export default function DashboardPage() {
  const { t, lang, setLang } = useLanguage();
  const { user, logout } = useAuth();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [sending, setSending] = useState(false);
  const [formData, setFormData] = useState({
    language: "en",
    notification_method: "email",
    active: true,
    topics: [] as number[],
  });
  const [message, setMessage] = useState("");
  const [kakaoMessage, setKakaoMessage] = useState("");

  useEffect(() => {
    if (!user) {
      router.push("/login");
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await getDashboardData();
        if (response.success && response.data) {
          setDashboardData(response.data);
          setFormData({
            language: response.data.language,
            notification_method: response.data.notification_method,
            active: response.data.active,
            topics: response.data.user_topics,
          });
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user, router]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const kakaoError = params.get("kakao_error");
    const kakaoSuccess = params.get("kakao_success");

    if (kakaoSuccess) {
      setKakaoMessage("Kakao account connected successfully!");
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    if (kakaoError) {
      setKakaoMessage("Failed to connect Kakao account");
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const response = await updatePreferences({
        topics: formData.topics,
        language: formData.language,
        notification_method: formData.notification_method,
        active: formData.active,
      });
      if (response.success) {
        setMessage("Preferences updated successfully!");
        const newData = await getDashboardData();
        if (newData.success && newData.data) setDashboardData(newData.data);
      } else {
        setMessage(response.message || "Failed to update preferences");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleConnectKakao = async () => {
    setMessage("");
    try {
      const response = await getKakaoAuthUrl();
      if (response.success && response.auth_url) {
        window.location.href = response.auth_url;
      } else {
        setMessage(response.message || "Failed to initiate Kakao connection");
      }
    } catch (error) {
      setMessage("Network error");
    }
  };

  const handleSendNow = async () => {
    setSending(true);
    setMessage("");
    try {
      const response = await sendWeeklyDigestNow();
      if (response.success) {
        setMessage("Weekly digest sent successfully!");
      } else {
        setMessage(response.message || "Failed to send digest");
      }
    } finally {
      setSending(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  if (loading || !dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm p-4 flex justify-between items-center border-b">
        <div className="flex items-center space-x-3">
          <div>
            <h1 className="text-xl font-bold text-gray-900">INSTWAVE</h1>
            <p className="text-sm text-gray-600">AI Research Paper Digest System</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <span className="mr-2 text-sm text-gray-700">{t("language")}:</span>
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="bg-white border border-gray-300 text-gray-700 px-2 py-1 rounded text-sm"
            >
              <option value="en">English</option>
              <option value="ko">한국어</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-700">{dashboardData.email}</span>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            className="border-gray-300 text-gray-700 hover:bg-gray-100"
            disabled={saving || sending}
          >
            {t("logout")}
          </Button>
        </div>
      </header>

      <div className="container mx-auto p-4 max-w-4xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">{t("dashboard_title")}</h1>
          <p className="text-gray-600 mt-1">Manage your research preferences and subscriptions</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${message.includes("success") ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            {message}
          </div>
        )}

        {kakaoMessage && (
          <div className={`mb-6 p-4 rounded-lg ${kakaoMessage.includes("success") ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            {kakaoMessage}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg">{t("notification_settings")}</CardTitle>
                <CardDescription className="text-gray-600">
                  Customize how you receive research updates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit}>
                  <div className="space-y-6">
                    <div>
                      <Label className="block mb-2 text-gray-700">{t("preferred_language")}</Label>
                      <Select value={formData.language} onValueChange={value => handleChange("language", value)} disabled={saving}>
                        <SelectTrigger className="w-full bg-white">
                          <SelectValue placeholder={t("select_language")} />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="en">{t("english")}</SelectItem>
                          <SelectItem value="ko">{t("korean")}</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label className="block mb-2 text-gray-700">{t("notification_method")}</Label>
                      <RadioGroup value={formData.notification_method} onValueChange={value => handleChange("notification_method", value)} className="space-y-2" disabled={saving}>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="email" id="email" />
                          <Label htmlFor="email" className="cursor-pointer text-gray-700">{t("email_only")}</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="kakao" id="kakao" />
                          <Label htmlFor="kakao" className="cursor-pointer text-gray-700">{t("kakao_only")}</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="both" id="both" />
                          <Label htmlFor="both" className="cursor-pointer text-gray-700">{t("both")}</Label>
                        </div>
                      </RadioGroup>
                    </div>

                    <div>
                      <Label className="block mb-2 text-gray-700">{t("kakao_account")}</Label>
                      <div className="mt-1">
                        {dashboardData.kakao_connected ? (
                          <div className="flex items-center">
                            <Badge className="bg-green-100 text-green-800">Connected</Badge>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-2">
                            <Badge className="bg-yellow-100 text-yellow-800">Not Connected</Badge>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={handleConnectKakao}
                              disabled={saving || dashboardData.kakao_connected}
                            >
                              {t("connect_kakao")}
                            </Button>
                          </div>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-2">{t("kakao_note")}</p>
                    </div>

                    <div className="flex items-center space-x-2 pt-2">
                      <Checkbox
                        id="active"
                        checked={formData.active}
                        onCheckedChange={checked => handleChange("active", checked)}
                        disabled={saving}
                      />
                      <Label htmlFor="active" className="cursor-pointer text-gray-700">
                        {t("receive_notifications")}
                      </Label>
                    </div>

                    <div className="pt-4">
                      <Button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-700"
                        disabled={saving}
                      >
                        {saving ? t("saving") : t("save_preferences")}
                      </Button>
                    </div>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          <div>
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="text-lg">{t("research_topics")}</CardTitle>
                <CardDescription className="text-gray-600">
                  {t("topic_selection_note")}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-3">
                  {dashboardData.all_topics.map(topic => (
                    <div
                      key={topic.id}
                      className="p-3 rounded-lg border cursor-pointer transition-all"
                      onClick={() => {
                        handleChange("topics",
                          formData.topics.includes(topic.id)
                            ? formData.topics.filter(id => id !== topic.id)
                            : [...formData.topics, topic.id]
                        );
                      }}
                    >
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id={`topic-${topic.id}`}
                          checked={formData.topics.includes(topic.id)}
                          className="pointer-events-none"
                        />
                        <Label
                          htmlFor={`topic-${topic.id}`}
                          className="cursor-pointer"
                        >
                          {topic.label}
                        </Label>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t("subscription_details")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label className="block text-gray-600 text-sm">{t("next_digest")}</Label>
                    <p className="font-medium text-gray-900">Tuesday, {dashboardData.next_tuesday}</p>
                  </div>

                  <Separator />

                  <div>
                    <Label className="block text-gray-600 text-sm">{t("status")}</Label>
                    <div className="flex items-center mt-1">
                      {dashboardData.active ? (
                        <Badge className="bg-green-100 text-green-800">{t("active")}</Badge>
                      ) : (
                        <Badge className="bg-gray-100 text-gray-800">{t("inactive")}</Badge>
                      )}
                    </div>
                  </div>

                  <Separator />

                  <Button
                    onClick={handleSendNow}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                    disabled={sending || !dashboardData.active}
                  >
                    {sending ? t("sending") : t("send_now")}
                  </Button>
                  <p className="text-xs text-center text-gray-500 mt-2">{t("send_note")}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
