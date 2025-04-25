"use client"

import { useState, useRef } from "react"
import Image from "next/image"
import { motion, useScroll, useTransform } from "framer-motion"
import { ArrowRight, Quote, Lightbulb, BookOpen, Compass, Share2, Bookmark, ThumbsUp } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"

// Sample musings data
const musings = [
  {
    id: "ceo-pilot",
    type: "story",
    title: "The CEO as a Pilot",
    content:
      "Being a CEO is akin to piloting an aircraft. It's not a single, decisive action that ensures a successful flight; rather, it's a continuous series of small adjustments and corrections. The CEO, like a pilot, is constantly making minor course corrections to keep the business on track towards its objectives. When executed effectively, these subtle adjustments are seamless, and the stakeholders remain unaware of the ongoing refinements.",
    image: "/cockpit-sunset-view.png",
    featured: true,
  },
  {
    id: "decision-making",
    type: "observation",
    title: "The Paradox of Decision-Making",
    content:
      "The most important decisions often feel the least urgent. While we rush to put out daily fires, the truly transformative choices—those that reshape our trajectory—rarely announce themselves with sirens. They whisper, waiting patiently for our attention.",
    image: "/foggy-fork.png",
  },
  {
    id: "buffett-quote",
    type: "quote",
    title: "On Reputation",
    content:
      '"It takes 20 years to build a reputation and five minutes to ruin it. If you think about that, you\'ll do things differently." - Warren Buffett',
    image: "/time-passing-desk.png",
  },
  {
    id: "feedback-loops",
    type: "observation",
    title: "Feedback Loops",
    content:
      "The most successful businesses create tight feedback loops between decision and consequence. The shorter this loop, the faster the learning, and the quicker the evolution. Companies that extend this gap—whether through bureaucracy or ego—inevitably fall behind.",
    image: "/blackboard-circular-arrows.png",
  },
  {
    id: "grove-quote",
    type: "quote",
    title: "On Paranoia",
    content: '"Only the paranoid survive." - Andy Grove',
    image: "/chess-midgame-control.png",
  },
  {
    id: "talent-story",
    type: "story",
    title: "The Talent Multiplier",
    content:
      "A-players hire A+ players. B-players hire C-players. The first rule of building a world-class organization is to understand that exceptional talent doesn't fear being outshined—they actively seek it. When you find leaders who instinctively surround themselves with people smarter than themselves, you've found the growth engines of your company.",
    image: "/collaborative-innovation.png",
  },
]

export default function BusinessMusingsPage() {
  const [activeTab, setActiveTab] = useState("all")
  const featuredRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: featuredRef,
    offset: ["start start", "end start"],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const y = useTransform(scrollYProgress, [0, 0.5], [0, 50])

  const featuredMusing = musings.find((musing) => musing.featured)
  const filteredMusings =
    activeTab === "all"
      ? musings.filter((musing) => !musing.featured)
      : musings.filter((musing) => musing.type === activeTab && !musing.featured)

  return (
    <div className="min-h-screen bg-black">
      <MainNav />

      {/* Hero Section */}
      <div ref={featuredRef} className="relative h-[80vh] overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src={featuredMusing?.image || "/placeholder.svg"}
            alt="Featured business musing"
            fill
            className="object-cover brightness-50"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black"></div>
        </div>

        <motion.div
          style={{ opacity, y }}
          className="container relative z-10 mx-auto flex h-full flex-col items-center justify-center px-4 text-center"
        >
          <Badge className="mb-4 bg-purple-500/20 text-purple-300">Featured Insight</Badge>
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl">
            Business <span className="text-purple-400">Musings</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-zinc-300">
            Quotes, stories, and wisdom gathered from the business world
            <br />
            But the big catch is: they're not <em className="text-purple-400 italic">that</em> cheesy
          </p>

          <div className="mt-12 max-w-3xl">
            <Card className="border-purple-500/20 bg-black/80 backdrop-blur-sm">
              <CardContent className="p-8">
                <div className="mb-4 flex items-center gap-2">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/20 text-purple-400">
                    <Compass className="h-5 w-5" />
                  </div>
                  <h2 className="text-2xl font-bold text-white">{featuredMusing?.title}</h2>
                </div>
                <p className="text-lg italic text-zinc-300">{featuredMusing?.content}</p>
                <div className="mt-6 flex justify-end">
                  <div className="flex gap-3">
                    <Button variant="ghost" size="icon" className="rounded-full text-zinc-400 hover:text-purple-400">
                      <Bookmark className="h-5 w-5" />
                    </Button>
                    <Button variant="ghost" size="icon" className="rounded-full text-zinc-400 hover:text-purple-400">
                      <ThumbsUp className="h-5 w-5" />
                    </Button>
                    <Button variant="ghost" size="icon" className="rounded-full text-zinc-400 hover:text-purple-400">
                      <Share2 className="h-5 w-5" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>

        <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-black to-transparent"></div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-16">
        <div className="mx-auto max-w-6xl">
          {/* Filter Tabs */}
          <div className="mb-12 flex flex-col items-center justify-center gap-4">
            <h2 className="text-3xl font-bold text-white">Explore Musings</h2>
            <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="bg-zinc-900">
                <TabsTrigger value="all" className="data-[state=active]:bg-purple-900 data-[state=active]:text-white">
                  All
                </TabsTrigger>
                <TabsTrigger value="story" className="data-[state=active]:bg-purple-900 data-[state=active]:text-white">
                  Stories
                </TabsTrigger>
                <TabsTrigger value="quote" className="data-[state=active]:bg-purple-900 data-[state=active]:text-white">
                  Quotes
                </TabsTrigger>
                <TabsTrigger
                  value="observation"
                  className="data-[state=active]:bg-purple-900 data-[state=active]:text-white"
                >
                  Observations
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {/* Musings Grid */}
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {filteredMusings.map((musing) => (
              <motion.div
                key={musing.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Card className="h-full overflow-hidden border-zinc-800 bg-zinc-900/50 transition-all duration-300 hover:-translate-y-1 hover:border-purple-500/30 hover:bg-zinc-900/70">
                  <CardContent className="p-0">
                    <div className="relative aspect-video overflow-hidden">
                      <Image
                        src={musing.image || "/placeholder.svg"}
                        alt={musing.title}
                        fill
                        className="object-cover transition-transform duration-500 hover:scale-105"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
                      <div className="absolute right-3 top-3">
                        <Badge className="bg-purple-500/20 text-purple-300">
                          {musing.type === "story" ? "Story" : musing.type === "quote" ? "Quote" : "Observation"}
                        </Badge>
                      </div>
                    </div>
                    <div className="p-6">
                      <div className="mb-3 flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/10 text-purple-400">
                          {musing.type === "story" ? (
                            <BookOpen className="h-4 w-4" />
                          ) : musing.type === "quote" ? (
                            <Quote className="h-4 w-4" />
                          ) : (
                            <Lightbulb className="h-4 w-4" />
                          )}
                        </div>
                        <h3 className="text-xl font-bold text-white">{musing.title}</h3>
                      </div>
                      <p className={`mb-4 text-sm text-zinc-400 ${musing.type === "quote" ? "italic" : ""}`}>
                        {musing.content.length > 180 ? `${musing.content.substring(0, 180)}...` : musing.content}
                      </p>
                      <div className="flex justify-between">
                        <Button variant="link" className="p-0 text-purple-400 hover:text-purple-300">
                          Read more
                          <ArrowRight className="ml-1 h-4 w-4" />
                        </Button>
                        <div className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 rounded-full text-zinc-400 hover:text-purple-400"
                          >
                            <Bookmark className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 rounded-full text-zinc-400 hover:text-purple-400"
                          >
                            <Share2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Empty State */}
          {filteredMusings.length === 0 && (
            <div className="mt-12 text-center">
              <p className="text-lg text-zinc-400">No musings found in this category.</p>
              <Button className="mt-4 bg-purple-600 hover:bg-purple-700" onClick={() => setActiveTab("all")}>
                View All Musings
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Newsletter Section */}
      <div className="border-t border-zinc-800 bg-gradient-to-br from-zinc-900 to-purple-950/30">
        <div className="container mx-auto px-4 py-16">
          <div className="mx-auto max-w-3xl rounded-xl border border-purple-500/20 bg-black/50 p-8 backdrop-blur-md">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white">Never Miss an Insight</h2>
              <p className="mt-2 text-zinc-400">Subscribe to receive new business musings directly in your inbox.</p>
              <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                <input
                  type="email"
                  placeholder="Your email address"
                  className="flex-1 rounded-md border border-zinc-800 bg-zinc-900 px-4 py-2 text-white focus:border-purple-500 focus:outline-none"
                />
                <Button className="bg-purple-600 hover:bg-purple-700">Subscribe</Button>
              </div>
              <p className="mt-4 text-xs text-zinc-500">We respect your privacy. Unsubscribe at any time.</p>
            </div>
          </div>
        </div>
      </div>

      <SiteFooter />
    </div>
  )
}
