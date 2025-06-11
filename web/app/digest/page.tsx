import { PaperList } from "@/components/paper-list"
import { mockPapers } from "@/lib/mock-papers"

export default function DigestPage() {
  // In a real application, you would fetch this data from your backend API.
  // For now, we use the mock data directly.
  const papers = mockPapers

  return (
    <main className="bg-gray-50 min-h-screen">
      <PaperList papers={papers} />
    </main>
  )
}
