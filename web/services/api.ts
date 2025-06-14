const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface ApiResponse {
  success: boolean;
  message?: string;
  user?: any;
  user_id?: number;
  data?: any;
  auth_url?: string;
  topics?: any[];
}

export const login = async (email: string, password: string): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ email, password }),
      credentials: "include",
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Network error. Please try again later." };
  }
};

export const register = async (name: string, email: string, password: string, topics: number[]): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/register`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ name, email, password, topics }),
      credentials: "include",
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Network error. Please try again later." };
  }
};

export const getDashboardData = async (): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
      method: "GET",
      credentials: "include",
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Failed to load dashboard data. Please try again." };
  }
};

export const getTopics = async (): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/topics`, {
      method: "GET",
      credentials: "include",
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Failed to get topics. Please try again." };
  }
};

export const updatePreferences = async (preferences: {
  topics: number[];
  language: string;
  notification_method: string;
  active: boolean;
}): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/update_preferences`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(preferences),
      credentials: "include",
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Failed to update preferences. Please try again." };
  }
};

export const sendWeeklyDigestNow = async (): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/send_digest_now`, {
      method: "POST",
      credentials: "include",
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Failed to send digest. Please try again." };
  }
};

export const logout = async (): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/logout`, {
      method: "POST",
      credentials: "include",
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Logout failed. Please try again." };
  }
};

export const getKakaoAuthUrl = async (): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/kakao_auth`, {
      method: "GET",
      credentials: "include",
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Failed to get Kakao auth URL" };
  }
};
