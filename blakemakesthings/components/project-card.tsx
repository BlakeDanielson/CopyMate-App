"use client"

import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"

import { Card, CardContent } from "@/components/ui/card"

interface ProjectCardProps {
  title: string
  description: string
  image: string
  link: string
  tags?: string[]
}

export function ProjectCard({ title, description, image, link, tags }: ProjectCardProps) {
  return (
    <motion.div whileHover={{ y: -5 }} transition={{ duration: 0.3 }}>
      <Link href={link}>
        <Card className="w-[300px] overflow-hidden border-zinc-800 bg-zinc-900/50 transition-colors hover:border-purple-500/50 hover:bg-zinc-900">
          <div className="relative aspect-video overflow-hidden">
            <Image
              src={image || "/placeholder.svg"}
              alt={title}
              fill
              className="object-cover transition-all duration-300 hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 transition-opacity hover:opacity-100"></div>
          </div>
          <CardContent className="p-4">
            <h3 className="line-clamp-1 text-lg font-bold text-white">{title}</h3>
            <p className="line-clamp-2 mt-1 text-sm text-zinc-400">{description}</p>
            {tags && tags.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-300">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  )
}
