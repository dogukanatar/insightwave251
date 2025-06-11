"use server"

import { mockNotifications } from "@/lib/mock-data"

interface Notification {
  id: string
  userEmail: string
  channelType: string
  content: string
  status: "sent" | "failed"
  sentAt: string // ISO 8601 string
}

/**
 * Simulates fetching recent notifications from the backend.
 * In a real application, this would call your Flask backend's endpoint for notification logs.
 */
export async function getRecentNotifications(): Promise<{ success: boolean; data: Notification[]; message?: string }> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  try {
    // In a real application, you would send a request to your backend:
    // const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/notifications`, {
    //   method: "GET",
    // });
    // if (!response.ok) {
    //   const errorData = await response.json();
    //   throw new Error(errorData.message || "Failed to fetch notifications.");
    // }
    // const data = await response.json();
    // return { success: true, data: data.notifications };

    // For mock purposes, return the mock data, sorted by sentAt descending
    const sortedNotifications = [...mockNotifications].sort(
      (a, b) => new Date(b.sentAt).getTime() - new Date(a.sentAt).getTime(),
    )
    return { success: true, data: sortedNotifications }
  } catch (error) {
    console.error("Error fetching notifications:", error)
    return { success: false, data: [], message: "Failed to load recent notifications." }
  }
}
