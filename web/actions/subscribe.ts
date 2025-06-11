"use server"

/**
 * Handles the subscription form submission.
 * Simulates a POST request to the /submit endpoint.
 * @param formData - The form data submitted by the user.
 * @returns {Promise<{status: string, message: string}>} The response from the backend.
 */
export async function subscribeAction(formData: FormData) {
  const name = formData.get("name") as string
  const email = formData.get("email") as string
  const topics = formData.getAll("topics") as string[]
  const channels = formData.getAll("channels") as string[] // New: Get selected channels

  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  try {
    // In a real application, you would send this data to your Flask backend:
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/submit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, topics, channels }), // New: Include channels in payload
    })

    if (!response.ok) {
      const errorData = await response.json()
      return { status: "error", message: errorData.message || "Submission failed." }
    }

    const data = await response.json()
    return data // Expected: { status: 'success', message: 'Subscription received!' }
  } catch (error) {
    console.error("Error submitting form:", error)
    return { status: "error", message: "An unexpected error occurred." }
  }
}
