"use client"
import { useAuth } from "@/context/AuthContext";
import { useLanguage } from "@/context/LanguageContext";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/Logo";

export function AppHeader({ showUser = false }) {
  const { t, lang, setLang } = useLanguage();
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <header className="bg-white shadow-sm p-4 flex justify-between items-center border-b">
      <Logo />

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

        {showUser && user && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-700">{user.email}</span>
            <Button
              onClick={handleLogout}
              variant="outline"
              className="border-gray-300 text-gray-700 hover:bg-gray-100"
            >
              {t("logout")}
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
