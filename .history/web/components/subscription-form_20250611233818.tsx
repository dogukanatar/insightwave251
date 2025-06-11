"use client"

import { useState, useEffect } from "react"
import { useActionState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { subscribeAction } from "@/actions/subscribe"

const topics = [
  { id: "ai", label: "AI", value: "AI" },
  { id: "ml", label: "ML", value: "ML" },
  { id: "robotics", label: "Robotics", value: "Robotics" },
  { id: "nlp", label: "NLP", value: "NLP" },
  { id: "data-science", label: "Data Science", value: "Data Science" },
]

const channels = [
  { id: "channel-email", label: "Email", value: "email" },
  { id: "channel-kakao", label: "KakaoTalk", value: "kakao" },
]

export default function SubscriptionForm() {
  const [state, formAction, isPending] = useActionState(subscribeAction, null)
  const [showConfirmation, setShowConfirmation] = useState(false)

  useEffect(() => {
    if (state?.status === "success") {
      setShowConfirmation(true)
    }
  }, [state])

  const handleCloseConfirmation = () => {
    setShowConfirmation(false)
    // Optionally reset the form here if needed
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md rounded-xl shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-gray-900">Subscribe to Research Updates</CardTitle>
          <CardDescription className="mt-2 text-sm text-gray-600">
            Stay informed with the latest breakthroughs in your favorite fields.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form action={formAction} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="font-semibold text-gray-700">
                Name
              </Label>
              <Input
                id="name"
                name="name"
                type="text"
                placeholder="John Doe"
                required
                className="rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email" className="font-semibold text-gray-700">
                Email
              </Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="john.doe@example.com"
                required
                className="rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-gray-800">Select Topics</h3>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                {topics.map((topic) => (
                  <div key={topic.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={topic.id}
                      name="topics"
                      value={topic.value}
                      className="h-5 w-5 rounded-md border-gray-300 text-blue-600 focus:ring-blue-500 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white hover:border-blue-400"
                    />
                    <Label
                      htmlFor={topic.id}
                      className="cursor-pointer text-sm font-medium text-gray-700 hover:text-blue-600"
                    >
                      {topic.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* New: Preferred Notification Channels section */}
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-gray-800">Preferred Notification Channels</h3>
              <div className="flex flex-wrap gap-4">
                {channels.map((channel) => (
                  <div key={channel.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={channel.id}
                      name="channels"
                      value={channel.value}
                      className="h-5 w-5 rounded-md border-gray-300 text-blue-600 focus:ring-blue-500 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white hover:border-blue-400"
                    />
                    <Label
                      htmlFor={channel.id}
                      className="cursor-pointer text-sm font-medium text-gray-700 hover:text-blue-600"
                    >
                      {channel.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <Button
              type="submit"
              className="w-full rounded-lg bg-blue-600 py-2 text-lg font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              disabled={isPending}
            >
              {isPending ? "Subscribing..." : "Subscribe"}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="text-center text-sm text-gray-500">
          We respect your privacy. You can unsubscribe at any time.
        </CardFooter>
      </Card>

      <Dialog open={showConfirmation} onOpenChange={setShowConfirmation}>
        <DialogContent className="sm:max-w-[425px] rounded-xl p-6 text-center">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-green-600">Thank you for subscribing!</DialogTitle>
            <DialogDescription className="mt-2 text-gray-700">
              {state?.message || "You have successfully subscribed to our research updates."}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            <Button onClick={handleCloseConfirmation} className="rounded-lg bg-blue-600 hover:bg-blue-700">
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
