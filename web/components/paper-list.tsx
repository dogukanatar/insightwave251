"use client"

import { useState } from "react"
import { PaperCard } from "./paper-card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"

interface Paper {
  title: string
  authors: string[]
  date: string
  summary: string
  link: string
}

interface PaperListProps {
  papers: Paper[]
}

export function PaperList({ papers }: PaperListProps) {
  const [selectedTopic, setSelectedTopic] = useState("all")

  const availableTopics = [
    { value: "all", label: "All Topics" },
    { value: "AI", label: "AI" },
    { value: "ML", label: "ML" },
    { value: "Robotics", label: "Robotics" },
    { value: "NLP", label: "NLP" },
    { value: "Data Science", label: "Data Science" },
  ]

  const filteredPapers = papers.filter((paper) => {
    if (selectedTopic === "all") return true
    // Simple topic filtering based on title for mock data.
    // In a real app, papers would have a 'topics' array to filter against.
    return paper.title.toLowerCase().includes(selectedTopic.toLowerCase())
  })

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h1 className="text-4xl font-extrabold text-gray-900">Daily Research Digest</h1>
        <div className="flex items-center gap-2">
          <Label htmlFor="topic-filter" className="sr-only">
            Filter by Topic
          </Label>
          <Select value={selectedTopic} onValueChange={setSelectedTopic}>
            <SelectTrigger
              id="topic-filter"
              className="w-[180px] rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            >
              <SelectValue placeholder="Filter by Topic" />
            </SelectTrigger>
            <SelectContent>
              {availableTopics.map((topic) => (
                <SelectItem key={topic.value} value={topic.value}>
                  {topic.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {filteredPapers.length === 0 ? (
        <p className="text-center text-gray-600 text-lg">No papers found for the selected topic.</p>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
          {filteredPapers.map((paper, index) => (
            <PaperCard key={index} {...paper} />
          ))}
        </div>
      )}
    </div>
  )
}
