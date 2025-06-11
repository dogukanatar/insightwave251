"use server"

import { mockThesisSummaries } from "@/lib/mock-data"

/**
 * Simulates fetching thesis paper summaries from the backend.
 * In a real application, this would call your Flask backend's endpoint for thesis data.
 */
export async function getThesisSummaries() {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  try {
    // In a real application, you would send a request to your backend:
    // const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/thesis-summaries`, {
    //   method: "GET",
    // });
    // if (!response.ok) {
    //   const errorData = await response.json();
    //   throw new Error(errorData.message || "Failed to fetch thesis summaries.");
    // }
    // const data = await response.json();
    // return { success: true, data: data.summaries };

    // For mock purposes, return the mock data
    return { success: true, data: mockThesisSummaries }
  } catch (error) {
    console.error("Error fetching thesis summaries:", error)
    return { success: false, data: [], message: "Failed to load thesis summaries." }
  }
}
