"use client"
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { getTopics } from "@/services/api";

interface Topic {
  id: number;
  label: string;
}

export default function RegisterPage() {
  const { t, lang, setLang } = useLanguage();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<number[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingTopics, setLoadingTopics] = useState(true);
  const { register } = useAuth();
  const router = useRouter();

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await getTopics();
        if (response.success && response.topics) {
          setTopics(response.topics);
        }
      } catch (err) {
        setError("Failed to load topics");
      } finally {
        setLoadingTopics(false);
      }
    };

    fetchTopics();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!name || !email || !password) {
      setError("All fields are required");
      return;
    }

    if (selectedTopics.length < 1) {
      setError(t("at_least_one_topic"));
      return;
    }

    setLoading(true);

    try {
      const result = await register(name, email, password, selectedTopics);
      if (!result.success) {
        setError(result.message || "Registration failed. Please try again.");
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const toggleTopic = (topicId: number) => {
    setSelectedTopics(prev =>
      prev.includes(topicId)
        ? prev.filter(id => id !== topicId)
        : [...prev, topicId]
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <div className="flex justify-end mb-4">
          <Select value={lang} onValueChange={setLang}>
            <SelectTrigger className="w-28">
              <SelectValue placeholder="Language" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="en">English</SelectItem>
              <SelectItem value="ko">한국어</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <h1 className="text-2xl font-bold mb-6 text-center">{t("register_title")}</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <Label htmlFor="name">{t("register_name")}</Label>
            <Input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="mb-4">
            <Label htmlFor="email">{t("register_email")}</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="mb-4">
            <Label htmlFor="password">{t("register_password")}</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
            <p className="text-xs text-gray-500 mt-1">
              {t("password_requirements")}
            </p>
          </div>

          <div className="mb-6">
            <Label>{t("research_topics")}</Label>
            <p className="text-sm text-gray-600 mb-2">
              {t("topic_selection_note")}
            </p>

            {loadingTopics ? (
              <div className="text-center py-4">Loading topics...</div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                {topics.map(topic => (
                  <div key={topic.id} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`topic-${topic.id}`}
                      checked={selectedTopics.includes(topic.id)}
                      onChange={() => toggleTopic(topic.id)}
                      className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      disabled={loading}
                    />
                    <label htmlFor={`topic-${topic.id}`} className="text-sm">
                      {topic.label}
                    </label>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={loading || loadingTopics}
          >
            {loading ? t("registering") : t("register_button")}
          </Button>
        </form>

        <div className="mt-4 text-center">
          <Link href="/login" className="text-blue-600 hover:underline">
            {t("register_login")}
          </Link>
        </div>
      </div>
    </div>
  );
}
