"use server"

import { revalidatePath } from "next/cache"

/**
 * Simulates triggering the daily digest.
 * In a real application, this would call your Flask backend's digest endpoint.
 */
export async function triggerDailyDigest() {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1000))

  try {
    // In a real application, you would send a request to your backend:
    // const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/trigger-digest`, {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    // });
    // if (!response.ok) {
    //   const errorData = await response.json();
    //   return { success: false, message: errorData.message || "Failed to trigger digest." };
    // }
    // const data = await response.json();
    // return { success: true, message: data.message || "Digest triggered successfully!" };

    // For mock purposes, we'll just return a success message
    const timestamp = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })
    const newLogEntry = `Digest sent to mock users at ${timestamp}`

    // In a real scenario, you might update a database or log file,
    // then revalidate the path to show the new log entry.
    revalidatePath("/admin") // Revalidate the admin page to show updated logs (if logs were dynamic)

    return { success: true, message: "Digest sent (mock)" }
  } catch (error) {
    console.error("Error triggering digest:", error)
    return { success: false, message: "An unexpected error occurred while triggering digest." }
  }
}
