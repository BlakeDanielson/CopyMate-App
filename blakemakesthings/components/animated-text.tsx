"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"

interface AnimatedTextProps {
  phrases: string[]
  interval?: number
  className?: string
  highlightClassName?: string
  prefix?: string
  suffix?: string
  inline?: boolean
}

export function AnimatedText({
  phrases,
  interval = 3000,
  className = "",
  highlightClassName = "text-purple-500",
  prefix = "",
  suffix = "",
  inline = false,
}: AnimatedTextProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const intervalId = setInterval(() => {
      setIsVisible(false)

      setTimeout(() => {
        setCurrentIndex((prevIndex) => (prevIndex + 1) % phrases.length)
        setIsVisible(true)
      }, 500) // Half a second for the fade out animation
    }, interval)

    return () => clearInterval(intervalId)
  }, [phrases, interval])

  return (
    <span className={`${className} ${inline ? "inline-flex items-center whitespace-nowrap" : "whitespace-nowrap"}`}>
      {prefix && <span className="whitespace-nowrap">{prefix}</span>}
      <AnimatePresence mode="wait">
        {isVisible && (
          <motion.span
            key={currentIndex}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.5 }}
            className={`${highlightClassName} whitespace-nowrap py-1 ${inline ? "ml-2" : ""}`}
          >
            {phrases[currentIndex]}
          </motion.span>
        )}
      </AnimatePresence>
      {suffix && <span className="whitespace-nowrap">{suffix}</span>}
    </span>
  )
}
