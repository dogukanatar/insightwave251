import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

interface Notification {
  id: string
  userEmail: string
  channelType: string
  content: string
  status: "sent" | "failed"
  sentAt: string // ISO 8601 string
}

interface NotificationsTableProps {
  notifications: Notification[]
}

export function NotificationsTable({ notifications }: NotificationsTableProps) {
  const formatTimestamp = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  const shortenContent = (text: string, maxLength = 100) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + "..."
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>User Email</TableHead>
            <TableHead>Channel</TableHead>
            <TableHead>Content</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Sent At</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {notifications.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="h-24 text-center text-gray-500">
                No recent notifications found.
              </TableCell>
            </TableRow>
          ) : (
            notifications.map((notification) => (
              <TableRow key={notification.id}>
                <TableCell className="font-medium">{notification.userEmail}</TableCell>
                <TableCell className="capitalize">{notification.channelType}</TableCell>
                <TableCell className="max-w-xs truncate">{shortenContent(notification.content)}</TableCell>
                <TableCell>
                  <Badge variant={notification.status === "sent" ? "default" : "destructive"} className="capitalize">
                    {notification.status}
                  </Badge>
                </TableCell>
                <TableCell>{formatTimestamp(notification.sentAt)}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
