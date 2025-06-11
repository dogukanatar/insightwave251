import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

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

export function ThesisSummaryCard({
  id,
  title,
  authors,
  summary,
  aiSummary,
  publishedDate,
  categories,
  sourceUrl,
}: ThesisSummary) {
  return (
    <Card className="flex flex-col h-full overflow-hidden">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-bold leading-tight text-gray-900">{title}</CardTitle>
        <CardDescription className="text-sm text-gray-600 mt-1">Authors: {authors.join(", ")}</CardDescription>
        <p className="text-xs text-gray-500 mt-1">Published: {publishedDate}</p>
      </CardHeader>
      <CardContent className="flex-grow space-y-2 text-sm">
        <div>
          <h3 className="font-semibold text-gray-800">Summary:</h3>
          <p className="text-gray-700 line-clamp-3">{summary}</p>
        </div>
        {aiSummary && (
          <div>
            <h3 className="font-semibold text-gray-800">AI Summary:</h3>
            <p className="text-gray-700 line-clamp-3">{aiSummary}</p>
          </div>
        )}
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center space-x-2">
            <Switch id={`audio-summary-${id}`} disabled />
            <Label htmlFor={`audio-summary-${id}`} className="text-sm font-medium text-gray-700">
              Audio Summary
            </Label>
          </div>
          <p className="text-xs text-gray-500">Audio coming soon</p>
        </div>
        <div className="flex flex-wrap gap-1 pt-2">
          {categories.map((category) => (
            <Badge key={category} variant="outline" className="text-xs">
              {category}
            </Badge>
          ))}
        </div>
      </CardContent>
      <CardFooter className="mt-auto pt-0">
        <Button asChild variant="link" className="p-0 h-auto text-blue-600 hover:text-blue-700">
          <Link href={sourceUrl} target="_blank" rel="noopener noreferrer">
            Source URL
          </Link>
        </Button>
      </CardFooter>
    </Card>
  )
}
