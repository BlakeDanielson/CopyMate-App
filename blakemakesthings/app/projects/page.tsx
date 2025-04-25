"use client"

import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { ArrowRight, Filter, Music, BookOpen, Sparkles, Code, Layers, BrainCircuit } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"

// Project categories
const categories = ["All", "AI", "Music", "Web App", "NLP", "Data Viz"]

// Project data
const projects = [
  {
    title: "OurStories",
    description:
      "I created this bedtime story generator that makes children the stars of their own stories—complete with AI-generated images that incorporate their photos. A passion project that combines storytelling with cutting-edge AI.",
    image: "/forest-friends-picnic.png",
    category: "AI",
    tags: ["AI", "NLP", "Image Generation", "E-commerce"],
    link: "/projects/ourstories",
    featured: true,
    icon: <BookOpen className="h-5 w-5" />,
  },
  {
    title: "Music Production Analyzer",
    description:
      "I built this AI tool after spending countless hours watching production tutorials, wishing I could quickly extract specific techniques without watching entire videos.",
    image: "/audio-spectrum-display.png",
    category: "Music",
    tags: ["AI", "Music Production", "Content Analysis", "Audio Processing"],
    link: "/projects/music-production-analyzer",
    featured: false,
    icon: <Music className="h-5 w-5" />,
  },
  {
    title: "Constant-Craft",
    description:
      "During a weekend coding sprint, I recreated the popular Infinite Craft game as a technical challenge to sharpen my React skills.",
    image: "/mystical-alchemy-table.png",
    category: "Web App",
    tags: ["Web Game", "React", "Interactive", "Clone"],
    link: "/projects/constant-craft",
    featured: false,
    icon: <Sparkles className="h-5 w-5" />,
  },
  {
    title: "AI Content Generator",
    description:
      "I developed this tool to help marketing teams break through writer's block with AI that learns and adapts to their unique brand voice.",
    image: "/placeholder.svg?height=400&width=600",
    category: "NLP",
    tags: ["NLP", "React", "OpenAI", "Node.js"],
    link: "/projects/ai-content-generator",
    featured: false,
    icon: <Code className="h-5 w-5" />,
  },
  {
    title: "Predictive Analytics Dashboard",
    description:
      "One of my most impactful projects—transforming complex data into intuitive visualizations that helped executives make proactive decisions.",
    image: "/placeholder.svg?height=400&width=600",
    category: "Data Viz",
    tags: ["Data Viz", "React", "D3.js"],
    link: "/projects/predictive-analytics",
    featured: false,
    icon: <Layers className="h-5 w-5" />,
  },
  {
    title: "Conversational AI Assistant",
    description:
      "Inspired by my grandmother's struggles with technology, I built an AI companion that makes digital interactions feel more human.",
    image: "/placeholder.svg?height=400&width=600",
    category: "NLP",
    tags: ["NLP", "BERT", "React"],
    link: "/projects/conversational-ai",
    featured: false,
    icon: <BrainCircuit className="h-5 w-5" />,
  },
]

// Project Card Component
function ProjectCard({ project }) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <Link href={project.link}>
        <Card className="h-full overflow-hidden border-zinc-800 bg-zinc-900/50 transition-all duration-300 hover:-translate-y-1 hover:border-purple-500/30 hover:bg-zinc-900/70 hover:shadow-lg hover:shadow-purple-500/5">
          <CardContent className="p-0">
            <div className="relative aspect-video overflow-hidden">
              <Image
                src={project.image || "/placeholder.svg"}
                alt={project.title}
                fill
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
              <div className="absolute right-3 top-3">
                <Badge className="bg-purple-500/20 text-purple-300">{project.category}</Badge>
              </div>
            </div>
            <div className="p-6">
              <div className="mb-3 flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/10 text-purple-400">
                  {project.icon}
                </div>
                <h3 className="text-xl font-bold text-white">{project.title}</h3>
              </div>
              <p className="mb-4 text-sm text-zinc-400">{project.description}</p>
              <div className="mb-4 flex flex-wrap gap-2">
                {project.tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-zinc-800 px-2 py-1 text-xs text-zinc-300">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="flex items-center text-sm font-medium text-purple-400">
                View Project
                <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  )
}

// Featured Project Component
function FeaturedProject({ project }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative overflow-hidden rounded-xl border border-purple-500/20 bg-gradient-to-br from-zinc-900 to-black p-1"
    >
      <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(0deg,#000000,transparent)]"></div>
      <div className="relative grid gap-8 p-6 md:grid-cols-2 md:p-10">
        <div className="flex flex-col justify-center space-y-4">
          <Badge className="w-fit bg-purple-500/20 text-purple-300">{project.category}</Badge>
          <h2 className="text-3xl font-bold text-white">{project.title}</h2>
          <p className="text-zinc-400">{project.description}</p>
          <div className="flex flex-wrap gap-2">
            {project.tags.map((tag) => (
              <span key={tag} className="rounded-full bg-zinc-800 px-3 py-1 text-xs text-zinc-300">
                {tag}
              </span>
            ))}
          </div>
          <div className="pt-4">
            <Link href={project.link}>
              <Button className="bg-purple-600 hover:bg-purple-700">
                View Case Study
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
        <div className="relative aspect-video overflow-hidden rounded-lg border border-zinc-800">
          <Image src={project.image || "/placeholder.svg"} alt={project.title} fill className="object-cover" />
          <div className="absolute inset-0 bg-black/20 opacity-0 transition-opacity hover:opacity-100"></div>
        </div>
      </div>
    </motion.div>
  )
}

export default function ProjectsPage() {
  const [selectedCategory, setSelectedCategory] = useState("All")

  const featuredProject = projects.find((project) => project.featured)
  const filteredProjects =
    selectedCategory === "All"
      ? projects.filter((project) => !project.featured)
      : projects.filter((project) => project.category === selectedCategory && !project.featured)

  return (
    <div className="min-h-screen bg-black">
      <MainNav />

      {/* Header Section */}
      <div className="relative bg-zinc-900 pt-24">
        <div className="absolute inset-0 bg-grid-white/5 opacity-50"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 to-zinc-900"></div>

        <div className="container relative z-10 mx-auto px-4 py-16 text-center">
          <Badge className="mb-4 bg-purple-500/20 text-purple-300">My Portfolio</Badge>
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl">
            Projects That <span className="text-purple-400">Made an Impact</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-zinc-300">
            From executive dashboards that transformed decision-making to AI tools that solve real problems—these are
            the projects I'm most proud of.
          </p>

          <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-black to-transparent"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-6xl">
          {/* Featured Project */}
          {featuredProject && <FeaturedProject project={featuredProject} />}

          {/* Filter Categories */}
          <div className="mb-8 mt-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-zinc-400" />
              <span className="text-sm text-zinc-400">Filter by:</span>
            </div>
            <Tabs defaultValue="All" value={selectedCategory} onValueChange={setSelectedCategory}>
              <TabsList className="bg-zinc-900">
                {categories.map((category) => (
                  <TabsTrigger
                    key={category}
                    value={category}
                    className="data-[state=active]:bg-purple-900 data-[state=active]:text-white"
                  >
                    {category}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>

          {/* Projects Grid */}
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredProjects.map((project) => (
              <ProjectCard key={project.title} project={project} />
            ))}
          </div>

          {/* Empty State */}
          {filteredProjects.length === 0 && (
            <div className="mt-12 text-center">
              <p className="text-lg text-zinc-400">No projects found in this category.</p>
              <Button className="mt-4 bg-purple-600 hover:bg-purple-700" onClick={() => setSelectedCategory("All")}>
                View All Projects
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Call to Action */}
      <div className="border-t border-zinc-800 bg-gradient-to-br from-zinc-900 to-purple-950/30">
        <div className="container mx-auto px-4 py-16">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="text-3xl font-bold text-white">Have a project in mind?</h2>
            <p className="mt-4 text-zinc-400">
              I'm always looking for interesting challenges and creative collaborations. Whether you need help with data
              integration, process optimization, or building something entirely new—I'd love to hear about it.
            </p>
            <div className="mt-8">
              <Link href="/contact">
                <Button size="lg" className="bg-purple-600 hover:bg-purple-700">
                  Let's Work Together
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <SiteFooter />
    </div>
  )
}
