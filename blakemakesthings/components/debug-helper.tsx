"use client"

import { useEffect, useState } from "react"

export function DebugHelper() {
  const [htmlClasses, setHtmlClasses] = useState<string>("")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const htmlElement = document.documentElement
    setHtmlClasses(htmlElement.className)
  }, [])

  if (!mounted) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-xs overflow-hidden rounded-lg bg-black/80 p-4 text-xs text-white backdrop-blur">
      <div>
        <p><strong>HTML Classes:</strong> {htmlClasses}</p>
        <p><strong>Is Dark Class Present:</strong> {htmlClasses.includes('dark') ? 'Yes' : 'No'}</p>
        <p><strong>Current Window Width:</strong> {typeof window !== 'undefined' ? window.innerWidth : 'N/A'}px</p>
      </div>
    </div>
  )
} 