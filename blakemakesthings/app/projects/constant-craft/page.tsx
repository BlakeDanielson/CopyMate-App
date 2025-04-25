import Image from "next/image"
import Link from "next/link"
import { ArrowLeft, ExternalLink, Github, Calendar, Users, Sparkles, Code, Gamepad2, Share2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"

export default function ConstantCraftPage() {
  return (
    <div className="min-h-screen bg-black">
      <MainNav />

      <div className="container py-12 pt-24 md:py-24">
        <div className="mx-auto max-w-4xl">
          <Link
            href="/projects"
            className="inline-flex items-center text-sm text-zinc-400 transition-colors hover:text-purple-400"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>

          <div className="mt-8">
            <Badge className="mb-4 bg-purple-500/20 text-purple-300">Web App</Badge>
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">Constant-Craft</h1>
            <p className="mt-4 text-xl text-zinc-400">
              An interactive element combination game where players discover new items by combining existing ones.
            </p>
          </div>

          <div className="mt-8 overflow-hidden rounded-xl border border-zinc-800">
            <Image
              src="/mystical-alchemy-table.png"
              alt="Constant-Craft"
              width={1200}
              height={600}
              className="w-full object-cover"
            />
          </div>

          <div className="mt-12 grid gap-12 md:grid-cols-3">
            <div className="space-y-6 md:col-span-2">
              <div>
                <h2 className="text-2xl font-bold text-white">The Project</h2>
                <p className="mt-4 text-zinc-400">
                  Constant-Craft is a faithful recreation of the popular web game Infinite Craft, where players start
                  with basic elements like earth, water, fire, and air, and combine them to discover hundreds of new
                  items. The game encourages creativity and experimentation, with surprising and often humorous results
                  when different elements are combined.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">Implementation</h2>
                <p className="mt-4 text-zinc-400">
                  This project was built as a technical challenge to recreate the core functionality and user experience
                  of Infinite Craft. It features a clean, intuitive interface where players can drag and drop elements
                  to combine them, with new discoveries being added to their inventory. The game state is saved locally,
                  allowing players to continue their progress across sessions.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">Key Features</h2>
                <ul className="mt-4 space-y-2 text-zinc-400">
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Intuitive drag-and-drop interface for combining elements</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Hundreds of possible combinations to discover</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Local storage to save game progress</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Animated reactions when new elements are created</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Searchable element inventory</span>
                  </li>
                </ul>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">Technical Details</h2>
                <p className="mt-4 text-zinc-400">
                  The application was built with a focus on performance and user experience:
                </p>
                <ul className="mt-4 space-y-2 text-zinc-400">
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>React with Next.js for the frontend framework</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Tailwind CSS for styling and responsive design</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>React DnD for drag-and-drop functionality</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Framer Motion for smooth animations and transitions</span>
                  </li>
                </ul>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="overflow-hidden rounded-lg border border-zinc-800">
                  <Image
                    src="/stylized-game-hud.png"
                    alt="Game interface"
                    width={400}
                    height={300}
                    className="aspect-[4/3] w-full object-cover"
                  />
                </div>
                <div className="overflow-hidden rounded-lg border border-zinc-800">
                  <Image
                    src="/atomic-assembly.png"
                    alt="Element combination animation"
                    width={400}
                    height={300}
                    className="aspect-[4/3] w-full object-cover"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-8">
              <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
                <h3 className="text-lg font-bold text-white">Project Details</h3>

                <div className="mt-4 space-y-4">
                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">My Role</p>
                      <p className="font-medium text-white">Full-Stack Developer</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">Timeline</p>
                      <p className="font-medium text-white">2 weeks</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">Team Size</p>
                      <p className="font-medium text-white">Solo project</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <p className="text-sm text-zinc-500">Technologies</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Badge variant="outline" className="border-zinc-700">
                      React
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      Next.js
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      Tailwind CSS
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      React DnD
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      Framer Motion
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      LocalStorage
                    </Badge>
                  </div>
                </div>

                <div className="mt-6 flex flex-col gap-3">
                  <Link href="#" target="_blank" rel="noopener noreferrer">
                    <Button className="w-full bg-purple-600 hover:bg-purple-700">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Play Constant-Craft
                    </Button>
                  </Link>
                  <Link href="https://github.com/BlakeDanielson" target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" className="w-full border-zinc-700">
                      <Github className="mr-2 h-4 w-4" />
                      View Source Code
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
                <h3 className="text-lg font-bold text-white">Learning Outcomes</h3>
                <ul className="mt-4 space-y-3 text-zinc-400">
                  <li className="flex items-start">
                    <Code className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Implementing complex drag-and-drop interfaces</span>
                  </li>
                  <li className="flex items-start">
                    <Gamepad2 className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Game state management and persistence</span>
                  </li>
                  <li className="flex items-start">
                    <Share2 className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Recreating existing UX with attention to detail</span>
                  </li>
                </ul>
              </div>

              <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
                <h3 className="text-lg font-bold text-white">Future Enhancements</h3>
                <ul className="mt-4 space-y-2 text-zinc-400">
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Cloud save functionality</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Social sharing of discoveries</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Achievement system</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Mobile-optimized interface</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="mt-16 flex justify-between">
            <Link href="/projects">
              <Button variant="outline" className="border-zinc-700">
                <ArrowLeft className="mr-2 h-4 w-4" />
                All Projects
              </Button>
            </Link>
            <Link href="/contact">
              <Button className="bg-purple-600 hover:bg-purple-700">Discuss a Project</Button>
            </Link>
          </div>
        </div>
      </div>

      <SiteFooter />
    </div>
  )
}
