"use client"

import { useEffect, useState } from "react"
import { ChevronDown } from "lucide-react"

interface ScrollIndicatorProps {
  className?: string
}

export function ScrollIndicator({ className = "" }: ScrollIndicatorProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 100) {
        setIsVisible(false)
      } else {
        setIsVisible(true)
      }
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const scrollDown = () => {
    window.scrollTo({
      top: window.innerHeight,
      behavior: "smooth",
    })
  }

  if (!isVisible) return null

  return (
    <button
      onClick={scrollDown}
      className={`flex flex-col items-center gap-2 text-sm text-zinc-500 transition-opacity hover:text-teal-600 dark:text-zinc-400 dark:hover:text-teal-400 ${className} ${
        isVisible ? "opacity-100" : "opacity-0"
      }`}
    >
      <span>Scroll</span>
      <ChevronDown className="h-4 w-4 animate-bounce" />
    </button>
  )
}
