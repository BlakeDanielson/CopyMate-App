import Link from "next/link"
import { ArrowLeft } from "lucide-react"

import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="container flex h-[calc(100vh-4rem)] flex-col items-center justify-center">
      <div className="mx-auto max-w-md text-center">
        <h1 className="text-9xl font-bold text-teal-500">404</h1>
        <h2 className="mt-4 text-2xl font-bold">Page Not Found</h2>
        <p className="mt-4 text-zinc-600 dark:text-zinc-400">
          Sorry, the page you're looking for doesn't exist or has been moved.
        </p>
        <Link href="/" className="mt-8 inline-block">
          <Button className="flex items-center gap-2 bg-teal-600 hover:bg-teal-700 dark:bg-teal-600 dark:hover:bg-teal-700">
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  )
}
