import Link from "next/link"
import Image from "next/image"
import { ArrowRight } from "lucide-react"

interface ProjectPreviewProps {
  title: string
  description: string
  image: string
  category: string
  slug: string
}

export function ProjectPreview({ title, description, image, category, slug }: ProjectPreviewProps) {
  return (
    <Link
      href={`/projects/${slug}`}
      className="group relative flex flex-col overflow-hidden rounded-lg border border-zinc-200 bg-white transition-all hover:-translate-y-1 hover:shadow-md dark:border-zinc-800 dark:bg-zinc-800/50"
    >
      <div className="relative aspect-[4/3] overflow-hidden">
        <Image
          src={image || "/placeholder.svg"}
          alt={title}
          fill
          className="object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 transition-opacity group-hover:opacity-100"></div>
      </div>
      <div className="flex flex-1 flex-col p-6">
        <div className="mb-2 text-xs font-medium uppercase tracking-wider text-teal-600 dark:text-teal-400">
          {category}
        </div>
        <h3 className="text-xl font-bold">{title}</h3>
        <p className="mt-2 flex-1 text-sm text-zinc-600 dark:text-zinc-400">{description}</p>
        <div className="mt-4 flex items-center text-sm font-medium text-teal-600 dark:text-teal-400">
          View Project
          <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
        </div>
      </div>
    </Link>
  )
}
