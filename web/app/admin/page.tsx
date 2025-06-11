import { AdminDashboard } from "@/components/admin-dashboard"
import { mockSubscribers, mockSystemLogs } from "@/lib/mock-data"
import { getThesisSummaries } from "@/actions/thesis-summaries"
import { getRecentNotifications } from "@/actions/notifications" // Import the new action

export default async function AdminPage() {
  const subscribers = mockSubscribers
  const systemLogs = mockSystemLogs

  // Fetch initial thesis summaries using the Server Action
  const thesisSummariesResult = await getThesisSummaries()
  const initialThesisSummaries = thesisSummariesResult.success ? thesisSummariesResult.data : []

  // Fetch initial notifications using the new Server Action
  const notificationsResult = await getRecentNotifications()
  const initialNotifications = notificationsResult.success ? notificationsResult.data : []

  return (
    <main className="bg-gray-50 min-h-screen">
      <AdminDashboard
        subscribers={subscribers}
        initialThesisSummaries={initialThesisSummaries}
        initialNotifications={initialNotifications} // Pass initial notifications
        systemLogs={systemLogs}
      />
    </main>
  )
}
