import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface PaperCardProps {
  title: string
  authors: string[]
  date: string
  summary: string
  link: string
}

export function PaperCard({ title, authors, date, summary, link }: PaperCardProps) {
  return (
    <Card className="flex flex-col h-full overflow-hidden">
      <CardHeader>
        <CardTitle className="text-xl font-bold leading-tight text-gray-900">{title}</CardTitle>
        <CardDescription className="text-sm text-gray-600 mt-1">Authors: {authors.join(", ")}</CardDescription>
        <p className="text-xs text-gray-500 mt-1">Published: {date}</p>
      </CardHeader>
      <CardContent className="flex-grow">
        <h3 className="font-semibold text-gray-800 mb-2">AI Summary</h3>
        <p className="text-sm text-gray-700 line-clamp-5">{summary}</p>
      </CardContent>
      <CardFooter className="mt-auto">
        <Button asChild className="w-full bg-blue-600 hover:bg-blue-700">
          <Link href={link} target="_blank" rel="noopener noreferrer">
            View Full Paper
          </Link>
        </Button>
      </CardFooter>
    </Card>
  )
}
