import Image from "next/image"
import Link from "next/link"
import { ArrowLeft, ExternalLink, Github, Calendar, Users, Sparkles, Music, Headphones, Video } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"

export default function MusicProductionAnalyzerPage() {
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
            <Badge className="mb-4 bg-purple-500/20 text-purple-300">Music</Badge>
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">Music Production Analyzer</h1>
            <p className="mt-4 text-xl text-zinc-400">
              An AI tool that analyzes dense and long music production videos and podcasts to extract specific tips and
              techniques.
            </p>
          </div>

          <div className="mt-8 overflow-hidden rounded-xl border border-zinc-800">
            <Image
              src="/audio-spectrum-display.png"
              alt="Music Production Analyzer"
              width={1200}
              height={600}
              className="w-full object-cover"
            />
          </div>

          <div className="mt-12 grid gap-12 md:grid-cols-3">
            <div className="space-y-6 md:col-span-2">
              <div>
                <h2 className="text-2xl font-bold text-white">The Challenge</h2>
                <p className="mt-4 text-zinc-400">
                  Music production tutorials and podcasts are often lengthy and packed with valuable information, but
                  finding specific techniques or tips can be time-consuming. Producers and musicians need a way to
                  quickly extract relevant knowledge without watching hours of content.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">The Solution</h2>
                <p className="mt-4 text-zinc-400">
                  The Music Production Analyzer uses advanced AI to process audio and video content, identifying key
                  moments, techniques, and tips. It transcribes the content, analyzes the context, and categorizes
                  information into searchable segments. Users can quickly find specific production techniques, gear
                  recommendations, or creative approaches without watching entire videos.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">Key Features</h2>
                <ul className="mt-4 space-y-2 text-zinc-400">
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Intelligent content segmentation by topic and technique</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Searchable database of production tips and techniques</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Direct links to specific timestamps in source videos</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Personalized recommendations based on user interests</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Integration with popular DAWs for contextual learning</span>
                  </li>
                </ul>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">Technical Implementation</h2>
                <p className="mt-4 text-zinc-400">
                  The analyzer combines several AI technologies to process multimedia content effectively:
                </p>
                <ul className="mt-4 space-y-2 text-zinc-400">
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Speech-to-text transcription with music-specific terminology recognition</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>
                      Natural language processing to identify techniques, gear mentions, and creative approaches
                    </span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Audio analysis to detect demonstrations and examples</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Knowledge graph to connect related concepts and techniques</span>
                  </li>
                </ul>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="overflow-hidden rounded-lg border border-zinc-800">
                  <Image
                    src="/audio-spectrum-analysis.png"
                    alt="Audio analysis interface"
                    width={400}
                    height={300}
                    className="aspect-[4/3] w-full object-cover"
                  />
                </div>
                <div className="overflow-hidden rounded-lg border border-zinc-800">
                  <Image
                    src="/audio-workspace.png"
                    alt="Searchable database interface"
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
                      <p className="font-medium text-white">Lead Developer & AI Engineer</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">Timeline</p>
                      <p className="font-medium text-white">2023 - Present</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">Team Size</p>
                      <p className="font-medium text-white">3 people</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <p className="text-sm text-zinc-500">Technologies</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Badge variant="outline" className="border-zinc-700">
                      Python
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      TensorFlow
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      React
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      Next.js
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      FFmpeg
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      OpenAI API
                    </Badge>
                  </div>
                </div>

                <div className="mt-6 flex flex-col gap-3">
                  <Link href="#" target="_blank" rel="noopener noreferrer">
                    <Button className="w-full bg-purple-600 hover:bg-purple-700">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Try the Demo
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
                <h3 className="text-lg font-bold text-white">Target Users</h3>
                <ul className="mt-4 space-y-3 text-zinc-400">
                  <li className="flex items-start">
                    <Music className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Music producers looking to improve their skills</span>
                  </li>
                  <li className="flex items-start">
                    <Headphones className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Audio engineers seeking specific techniques</span>
                  </li>
                  <li className="flex items-start">
                    <Video className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Content creators making educational material</span>
                  </li>
                </ul>
              </div>

              <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
                <h3 className="text-lg font-bold text-white">User Testimonial</h3>
                <svg
                  className="h-8 w-8 text-zinc-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M7 16l-4-4m0 0l4-4m-4 4h18"
                  ></path>
                </svg>
                <p className="mt-4 italic text-zinc-400">
                  "This tool has completely transformed how I learn production techniques. I used to spend hours
                  watching tutorials to find specific information. Now I can search exactly what I need and jump right
                  to that part of the video."
                </p>
                <div className="mt-4">
                  <p className="font-medium text-white">Alex Chen</p>
                  <p className="text-sm text-zinc-500">Electronic Music Producer</p>
                </div>
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
