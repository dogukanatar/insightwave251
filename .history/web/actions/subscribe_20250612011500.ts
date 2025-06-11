"use server"

interface SubscribeState {
  status?: "success" | "error";
  message?: string;
  user_id?: number;
}

/**
 * Handles the subscription form submission.
 * Sends data to the Flask backend /submit endpoint.
 * @param prevState - Previous state from useActionState
 * @param formData - The form data submitted by the user.
 * @returns {Promise<SubscribeState>} The response from the backend.
 */
export async function subscribeAction(
  prevState: SubscribeState | null,
  formData: FormData
): Promise<SubscribeState> {
  const name = formData.get("name") as string
  const email = formData.get("email") as string
  const topics = formData.getAll("topics") as string[]

  // Server-side validation (backup for client-side validation)
  if (!name || !email) {
    return { 
      status: "error", 
      message: "Name and email are required." 
    }
  }

  if (topics.length < 3) {
    return { 
      status: "error", 
      message: "Please select at least 3 research topics." 
    }
  }

  // Validate topic IDs (should be 1-6)
  const validTopicIds = ["1", "2", "3", "4", "5", "6"]
  const invalidTopics = topics.filter(topic => !validTopicIds.includes(topic))
  if (invalidTopics.length > 0) {
    return { 
      status: "error", 
      message: `Invalid topic selection: ${invalidTopics.join(", ")}` 
    }
  }

  try {
    // Use the Flask backend API endpoint
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5001"
    
         // Create form data to match Flask backend expectations
     const formData = new URLSearchParams()
     formData.append('name', name)
     formData.append('email', email)
     
     // Add topics as multiple form fields
     topics.forEach(topic => {
       formData.append('topics', topic)
     })
     
     const response = await fetch(`${backendUrl}/submit`, {
       method: "POST",
       headers: {
         "Content-Type": "application/x-www-form-urlencoded",
       },
       body: formData.toString()
     })

    if (!response.ok) {
      let errorMessage = "Submission failed."
      
      try {
        const errorData = await response.json()
        errorMessage = errorData.message || errorMessage
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage
      }

      return { 
        status: "error", 
        message: errorMessage 
      }
    }

    const data = await response.json()
    
    // Handle successful response
    if (data.status === "success") {
      return {
        status: "success",
        message: data.message || "Subscription received!",
        user_id: data.user_id
      }
    } else {
      return {
        status: "error",
        message: data.message || "Subscription failed."
      }
    }

  } catch (error) {
    console.error("Error submitting subscription:", error)
    
    // Provide user-friendly error message
    if (error instanceof TypeError && error.message.includes("fetch")) {
      return { 
        status: "error", 
        message: "Unable to connect to the server. Please check your internet connection and try again." 
      }
    }
    
    return { 
      status: "error", 
      message: "An unexpected error occurred. Please try again later." 
    }
  }
}
