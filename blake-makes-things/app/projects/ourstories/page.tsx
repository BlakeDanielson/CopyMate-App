import Image from "next/image"
import Link from "next/link"
import { ArrowLeft, ExternalLink, Github, Calendar, Users, Sparkles, BookOpen, Camera, ShoppingBag } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"

export default function OurStoriesPage() {
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
            <Badge className="mb-4 bg-purple-500/20 text-purple-300">AI</Badge>
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">OurStories</h1>
            <p className="mt-4 text-xl text-zinc-400">
              A bedtime story generator that makes your child the star of the story, with AI-generated images and
              physical printing options.
            </p>
          </div>

          <div className="mt-8 overflow-hidden rounded-xl border border-zinc-800">
            <Image
              src="/forest-friends-picnic.png"
              alt="OurStories"
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
                  Parents want to create magical bedtime experiences for their children, but finding stories that truly
                  engage their kids can be difficult. Traditional books lack personalization, while simply making up
                  stories on the spot can be challenging for many parents.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">The Solution</h2>
                <p className="mt-4 text-zinc-400">
                  OurStories combines the best of both worlds: the convenience of "tell me a bedtime story" with the
                  tangible experience of "read me a bedtime story." The platform allows parents to generate personalized
                  stories featuring their child as the main character, complete with AI-generated illustrations that
                  incorporate actual photos of the child. These stories can be enjoyed digitally or ordered as physical
                  printed books.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">Key Features</h2>
                <ul className="mt-4 space-y-2 text-zinc-400">
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Personalized story generation based on child's name, interests, and preferences</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>AI image generation that incorporates uploaded photos of the child</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Digital story library for immediate reading on any device</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Print-on-demand service for high-quality physical storybooks</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Educational themes and moral lessons customized to parents' preferences</span>
                  </li>
                </ul>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">Technical Implementation</h2>
                <p className="mt-4 text-zinc-400">
                  OurStories leverages several cutting-edge AI technologies to create a seamless experience:
                </p>
                <ul className="mt-4 space-y-2 text-zinc-400">
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>GPT-4 for generating engaging, age-appropriate story narratives</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Stable Diffusion with LoRA fine-tuning for consistent character appearance</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Face swapping and image composition algorithms for natural integration of child photos</span>
                  </li>
                  <li className="flex items-start">
                    <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Print-ready PDF generation with professional layout templates</span>
                  </li>
                </ul>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="overflow-hidden rounded-lg border border-zinc-800">
                  <Image
                    src="/placeholder.svg?key=vmorq"
                    alt="Child reading personalized book"
                    width={400}
                    height={300}
                    className="aspect-[4/3] w-full object-cover"
                  />
                </div>
                <div className="overflow-hidden rounded-lg border border-zinc-800">
                  <Image
                    src="/whimsical-forest-friends.png"
                    alt="AI-generated storybook illustration"
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
                      <p className="font-medium text-white">Founder & Lead Developer</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">Timeline</p>
                      <p className="font-medium text-white">2022 - Present</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">Team Size</p>
                      <p className="font-medium text-white">4 people</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <p className="text-sm text-zinc-500">Technologies</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Badge variant="outline" className="border-zinc-700">
                      Next.js
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      OpenAI API
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      Stable Diffusion
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      AWS
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      Stripe
                    </Badge>
                    <Badge variant="outline" className="border-zinc-700">
                      Print API
                    </Badge>
                  </div>
                </div>

                <div className="mt-6 flex flex-col gap-3">
                  <Link href="#" target="_blank" rel="noopener noreferrer">
                    <Button className="w-full bg-purple-600 hover:bg-purple-700">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Visit OurStories
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
                    <BookOpen className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Parents seeking personalized bedtime stories</span>
                  </li>
                  <li className="flex items-start">
                    <Camera className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Families wanting to create unique keepsakes</span>
                  </li>
                  <li className="flex items-start">
                    <ShoppingBag className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                    <span>Gift-givers looking for meaningful presents</span>
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
                  "My daughter's face lit up when she saw herself in the story! She asks for her personalized books
                  every night now. The physical copy we ordered is beautiful and has become a treasured keepsake."
                </p>
                <div className="mt-4">
                  <p className="font-medium text-white">Sarah Johnson</p>
                  <p className="text-sm text-zinc-500">Parent of a 5-year-old</p>
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
