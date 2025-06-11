"use client"

import { useState, useEffect } from "react"
import { useActionState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { triggerDailyDigest } from "@/actions/admin"
import { getThesisSummaries } from "@/actions/thesis-summaries"
import { getRecentNotifications } from "@/actions/notifications" // Import the new action
import { ThesisSummaryCard } from "./thesis-summary-card"
import { NotificationsTable } from "./notifications-table" // Import the new component
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs" // Import Tabs components

interface Subscriber {
  id: string
  name: string
  email: string
  topics: string[]
  channels: string[]
}

interface ThesisSummary {
  id: string
  title: string
  authors: string[]
  summary: string
  aiSummary?: string
  publishedDate: string
  categories: string[]
  sourceUrl: string
}

interface Notification {
  id: string
  userEmail: string
  channelType: string
  content: string
  status: "sent" | "failed"
  sentAt: string // ISO 8601 string
}

interface AdminDashboardProps {
  subscribers: Subscriber[]
  initialThesisSummaries: ThesisSummary[]
  initialNotifications: Notification[] // New prop for initial notifications
  systemLogs: string[]
}

export function AdminDashboard({
  subscribers,
  initialThesisSummaries,
  initialNotifications,
  systemLogs,
}: AdminDashboardProps) {
  const { toast } = useToast()
  const [digestState, triggerDigestAction, isDigestPending] = useActionState(triggerDailyDigest, null)
  const [thesisSummaries, setThesisSummaries] = useState<ThesisSummary[]>(initialThesisSummaries)
  const [notifications, setNotifications] = useState<Notification[]>(initialNotifications) // State for notifications

  const [refreshSummariesState, refreshSummariesAction, isRefreshSummariesPending] = useActionState(
    getThesisSummaries,
    null,
  )
  const [refreshNotificationsState, refreshNotificationsAction, isRefreshNotificationsPending] = useActionState(
    getRecentNotifications,
    null,
  ) // New action state for notifications

  // Effect to update thesisSummaries when refreshSummariesState changes
  useEffect(() => {
    if (refreshSummariesState?.success) {
      setThesisSummaries(refreshSummariesState.data)
      toast({
        title: "Success",
        description: "Thesis summaries refreshed!",
        variant: "default",
      })
    } else if (refreshSummariesState && !refreshSummariesState.success) {
      toast({
        title: "Error",
        description: refreshSummariesState.message || "Failed to refresh summaries.",
        variant: "destructive",
      })
    }
  }, [refreshSummariesState, toast])

  // Effect to update notifications when refreshNotificationsState changes
  useEffect(() => {
    if (refreshNotificationsState?.success) {
      setNotifications(refreshNotificationsState.data)
      toast({
        title: "Success",
        description: "Notifications refreshed!",
        variant: "default",
      })
    } else if (refreshNotificationsState && !refreshNotificationsState.success) {
      toast({
        title: "Error",
        description: refreshNotificationsState.message || "Failed to refresh notifications.",
        variant: "destructive",
      })
    }
  }, [refreshNotificationsState, toast])

  // Show toast message after digest action completes
  if (digestState) {
    toast({
      title: digestState.success ? "Success" : "Error",
      description: digestState.message,
      variant: digestState.success ? "default" : "destructive",
    })
    // Reset state after showing toast to prevent re-showing on re-renders
    digestState.success = undefined
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-8 text-center text-4xl font-extrabold text-gray-900">Admin Dashboard</h1>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3 mb-8">
        {/* Digest Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Digest Controls</CardTitle>
            <CardDescription>Manually trigger the daily research digest.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={() => triggerDigestAction(new FormData())}
              disabled={isDigestPending}
              className="w-full bg-blue-600 py-2 text-lg font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {isDigestPending ? "Sending Digest..." : "Trigger Daily Digest Now"}
            </Button>
          </CardContent>
        </Card>

        {/* System Logs Panel */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-2xl font-bold">System Logs</CardTitle>
            <CardDescription>Recent system activities and events.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="max-h-64 overflow-y-auto rounded-md border bg-gray-50 p-4 text-sm">
              <ul className="space-y-2">
                {systemLogs.map((log, index) => (
                  <li key={index} className="text-gray-700">
                    • {log}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="subscribers" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="subscribers">Subscribers</TabsTrigger>
          <TabsTrigger value="thesis-summaries">Thesis Summaries</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>

        <TabsContent value="subscribers">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Subscribers</CardTitle>
              <CardDescription>Manage and view all subscribed users.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Topics</TableHead>
                      <TableHead>Channels</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {subscribers.map((subscriber) => (
                      <TableRow key={subscriber.id}>
                        <TableCell className="font-medium">{subscriber.name}</TableCell>
                        <TableCell>{subscriber.email}</TableCell>
                        <TableCell>{subscriber.topics.length > 0 ? subscriber.topics.join(", ") : "N/A"}</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {subscriber.channels.map((channel) => (
                              <Badge key={channel} variant="secondary" className="capitalize">
                                {channel}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="thesis-summaries">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
                <CardTitle className="text-2xl font-bold">Thesis Summaries</CardTitle>
                <CardDescription>List of AI-generated summaries from the thesis table.</CardDescription>
              </div>
              <Button
                onClick={() => refreshSummariesAction(new FormData())}
                disabled={isRefreshSummariesPending}
                className="bg-green-600 hover:bg-green-700"
              >
                {isRefreshSummariesPending ? "Refreshing..." : "Refresh Summaries"}
              </Button>
            </CardHeader>
            <CardContent>
              {thesisSummaries.length === 0 ? (
                <p className="text-center text-gray-600">No thesis summaries available.</p>
              ) : (
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {thesisSummaries.map((summary) => (
                    <ThesisSummaryCard key={summary.id} {...summary} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
                <CardTitle className="text-2xl font-bold">Recent Notifications</CardTitle>
                <CardDescription>List of recently sent messages to users.</CardDescription>
              </div>
              <Button
                onClick={() => refreshNotificationsAction(new FormData())}
                disabled={isRefreshNotificationsPending}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {isRefreshNotificationsPending ? "Refreshing..." : "Refresh Notifications"}
              </Button>
            </CardHeader>
            <CardContent>
              <NotificationsTable notifications={notifications} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
