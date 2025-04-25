"use client"

import type React from "react"

import { useRef } from "react"
import Image from "next/image"
import Link from "next/link"
import { motion, useScroll, useTransform } from "framer-motion"

interface HeroParallaxProps {
  items: {
    title: string
    link: string
    thumbnail: string
  }[]
  children: React.ReactNode
}

export function HeroParallax({ items, children }: HeroParallaxProps) {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  })

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"])
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])

  return (
    <div ref={ref} className="relative h-screen overflow-hidden bg-black">
      <motion.div style={{ y, opacity }} className="absolute inset-0 z-0">
        <div className="grid h-full grid-cols-2 gap-4 p-4 md:grid-cols-4 md:p-8">
          {items.map((item, i) => (
            <div
              key={i}
              className={`relative h-full overflow-hidden rounded-xl ${
                i % 2 === 0 ? "translate-y-8" : "-translate-y-8"
              }`}
            >
              <Link href={item.link}>
                <div className="group relative h-full w-full overflow-hidden rounded-xl border border-zinc-800" style={{ position: 'relative' }}>
                  <Image
                    src={item.thumbnail || "/placeholder.svg"}
                    alt={item.title}
                    fill
                    priority={i === 0}
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black/60 opacity-0 transition-opacity group-hover:opacity-100"></div>
                  <div className="absolute bottom-0 left-0 right-0 p-4 text-white opacity-0 transition-opacity group-hover:opacity-100">
                    <h3 className="text-lg font-bold">{item.title}</h3>
                  </div>
                </div>
              </Link>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Gradient overlay */}
      <div className="absolute inset-0 z-0 bg-gradient-to-b from-black/80 via-black/60 to-black"></div>

      {children}
    </div>
  )
}
