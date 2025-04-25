"use client"

import { useRef } from "react"
import Link from "next/link"
import Image from "next/image"
import { motion } from "framer-motion"
import { ArrowRight, ChevronDown, Sparkles, Mail, Phone, MapPin, Code } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"
import { HeroParallax } from "@/components/hero-parallax"
import { Badge } from "@/components/ui/badge"
import { AnimatedText } from "@/components/animated-text"
import { FeaturedMusicPlayer } from "@/components/featured-music-player"

export default function Home() {
  const aboutRef = useRef<HTMLDivElement>(null)

  const heroItems = [
    {
      title: "Abstract Gradient",
      link: "/projects/financial-modeling",
      thumbnail: "/hero-backgrounds/abstract-gradient.jpg",
    },
    {
      title: "Nature Landscape",
      link: "/projects/operational-efficiency",
      thumbnail: "/hero-backgrounds/nature-landscape.jpg",
    },
    {
      title: "Urban Geometric",
      link: "/projects/data-integration",
      thumbnail: "/hero-backgrounds/urban-geometric.jpg",
    },
    {
      title: "Tech Particles",
      link: "/projects/strategic-partnerships",
      thumbnail: "/hero-backgrounds/tech-particles.jpg",
    },
  ]

  // Identity/role phrases for animation - Keep original list for Hero section if needed elsewhere
  const identityPhrases = [
    "Product Manager",
    "Technical Softskiller",
    "Bandwidth Expander",
    "Pretty Chill Guy",
    "Entrepreneur",
    "Music Producer",
    "Great +1 to a Wedding",
    "Strategic Advisor",
    "Published Writer",
  ]

  return (
    <div className="flex min-h-screen flex-col bg-black">
      <MainNav />

      {/* Hero Section with Parallax */}
      <HeroParallax items={heroItems}>
        <div className="absolute inset-0 z-10 flex items-center justify-center">
          <div className="max-w-3xl text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-6"
            >
              <h1 className="text-3xl font-bold tracking-tight text-white text-animation-container sm:text-4xl md:text-5xl lg:text-6xl">
                <div className="flex flex-col items-center">
                  <span>Hi, I'm Blake, I'm a</span>
                  <div className="min-h-[1.5em] flex items-center justify-center">
                    {/* Keep original animated text here if desired */}
                    <AnimatedText phrases={identityPhrases} highlightClassName="text-purple-500" />
                  </div>
                </div>
              </h1>
              <p className="text-lg text-zinc-300 mt-6 font-medium">
                Aspiring Product Manager with a talent for building relationships across diverse teams and communicating
                technical concepts to any audience. Seeking to drive innovation at a fast-growing company making an
                actual difference.
              </p>
              <div className="flex flex-wrap justify-center gap-4 pt-4">
                <Button
                  size="lg"
                  className="group bg-purple-600 hover:bg-purple-700"
                  onClick={() => {
                    aboutRef.current?.scrollIntoView({ behavior: "smooth" })
                  }}
                >
                  About Me
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
                <Link href="/projects">
                  <Button
                    variant="outline"
                    size="lg"
                    className="border-zinc-800 bg-zinc-950/50 text-white backdrop-blur-sm hover:bg-zinc-900/50 hover:text-purple-300"
                  >
                    View Projects
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
        <div className="absolute bottom-10 left-1/2 z-10 -translate-x-1/2">
          <ChevronDown className="h-8 w-8 animate-bounce text-white opacity-70" />
        </div>
      </HeroParallax>

      {/* About Section - UPDATED */}
      <div ref={aboutRef} className="container mx-auto px-4 py-24">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12">
            <div className="flex flex-col items-center text-center mb-8">
              <Badge className="mb-2 bg-purple-500/20 text-purple-300">About Me</Badge>
              {/* Updated Headline */}
              <h2 className="text-3xl font-bold text-white mb-3">
                Results-Driven Product Enthusiast Bridging Finance and Technology
              </h2>
              <div className="w-24 h-1 bg-purple-500/50 rounded-full my-4"></div>
            </div>
          </div>

          <div className="grid gap-12 md:grid-cols-12">
            {/* Image Column - 5 columns on desktop */}
            <div className="md:col-span-5 relative">
              <div className="absolute -left-4 -top-4 h-24 w-24 rounded-full bg-purple-500/20 blur-2xl"></div>
              <div className="sticky top-24 relative aspect-[3/4] overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900 shadow-xl shadow-purple-900/10">
                <Image src="/blake_jacket.png" alt="Blake Danielson" fill className="object-contain" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                <div className="absolute bottom-6 left-6 right-6 rounded-lg border border-zinc-800 bg-zinc-900/90 p-4 backdrop-blur-sm shadow-lg">
                  <div className="flex items-center gap-3">
                    <Sparkles className="h-5 w-5 text-purple-500" />
                    {/* Updated Tagline */}
                    <span className="text-sm font-medium text-white">Finance & CS background driving product innovation</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Content Column - 7 columns on desktop - UPDATED CONTENT */}
            <div className="md:col-span-7 space-y-8"> {/* Increased spacing */}
              {/* Opening Summary */}
              <p className="text-lg text-zinc-300 leading-relaxed">
                With a unique foundation in Finance and Computer Science from the University of Denver, I specialize in bridging technical solutions with business strategy to drive growth, efficiency, and innovation.
              </p>

              {/* Experience Highlights */}
              <div>
                <h3 className="text-xl font-semibold text-white mb-4">Experience Highlights</h3>
                <ul className="space-y-3 text-zinc-400 list-disc list-inside pl-2"> {/* Added padding */}
                  <li>
                    Managed deployment of <span className="font-medium text-purple-400">$80 million</span> in strategic investments while working directly with the CEO of California's largest legal cannabis operator.
                  </li>
                  <li>
                    Developed executive dashboards and financial models that <span className="font-medium text-purple-400">transformed decision-making processes</span> for Fortune 50 partners.
                  </li>
                  <li>
                    Generated over <span className="font-medium text-purple-400">$100k in revenue</span> through data-driven newsletter strategies, leading to opportunities with high-profile venture capital like Casa Verde Capital.
                  </li>
                  <li>
                    Leveraged technical background to create automation solutions and database optimizations, significantly <span className="font-medium text-purple-400">improving efficiency and reducing costs</span>.
                  </li>
                   <li>
                    Founded a cryptocurrency arbitrage group and became a top-followed cannabis industry analyst on Seeking Alpha during university, demonstrating early entrepreneurial drive.
                  </li>
                </ul>
              </div>

              {/* Skills Integration / Callout */}
               <div className="bg-zinc-800/30 p-5 rounded-lg border-l-4 border-purple-500 shadow-inner">
                 <p className="text-zinc-300 leading-relaxed"> {/* Added leading-relaxed */}
                   My strength lies in translating complex technical concepts into actionable business insights and fostering collaboration across diverse technical and non-technical teams to deliver impactful results.
                 </p>
               </div>

              {/* Education Context */}
              <div>
                 <h3 className="text-xl font-semibold text-white mb-3">Foundation</h3>
                 <p className="text-zinc-400 leading-relaxed"> {/* Added leading-relaxed */}
                   Grounded in Finance and Computer Science from the University of Denver, my academic background provides a robust framework for analyzing problems from both business and technical perspectives.
                 </p>
              </div>

              {/* Call to Action */}
              <div className="flex flex-wrap gap-4 pt-4"> {/* Adjusted gap and padding */}
                <Link href="/my-story"> {/* Updated href */}
                  <Button className="group bg-purple-600 hover:bg-purple-700">
                    More About My Journey {/* Updated text */}
                    <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </Button>
                </Link>
                <Link href="/projects">
                  {/* Kept original styling for consistency, added hover effect */}
                  <Button variant="outline" className="border-zinc-700 text-white hover:bg-zinc-800 hover:text-purple-300">
                    View Projects
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          {/* Skills Section - UNCHANGED */}
          <div className="mt-16 grid gap-8 md:grid-cols-2">
            <Card className="border-zinc-800 bg-zinc-900/50 p-6 hover:border-purple-500/30 transition-colors">
              <div className="flex items-start gap-4 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/20 text-purple-400 mt-1">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Skills & Expertise</h3>
                  <p className="text-zinc-400 mb-4">Core competencies that drive my professional approach</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {[
                  "Financial Modeling",
                  "Product Management",
                  "Business Development",
                  "M&A Due Diligence",
                  "Strategic Partnerships",
                  "Investor Relations",
                  "Team Leadership",
                  "Process Optimization",
                ].map((skill) => (
                  <span key={skill} className="rounded-full bg-purple-500/10 px-3 py-1 text-sm text-purple-300">
                    {skill}
                  </span>
                ))}
              </div>
            </Card>

            <Card className="border-zinc-800 bg-zinc-900/50 p-6 hover:border-purple-500/30 transition-colors">
              <div className="flex items-start gap-4 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/20 text-purple-400 mt-1">
                  <Code className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white mb-2">Technologies</h3>
                  <p className="text-zinc-400 mb-4">Technical tools and platforms I work with</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {[
                  "SQL",
                  "Financial Analysis",
                  "Data Integration",
                  "Business Intelligence",
                  "Automation",
                  "CRM Systems",
                  "Excel/Google Sheets",
                  "Presentation Software",
                ].map((tech) => (
                  <span
                    key={tech}
                    className="rounded-full border border-zinc-700 bg-zinc-800 px-3 py-1 text-sm text-zinc-300"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </Card>
          </div>

          {/* Contact Information - UNCHANGED */}
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            <Card className="border-zinc-800 bg-zinc-900/50 p-6 hover:border-purple-500/30 transition-colors">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-500/20 text-purple-400">
                  <Mail className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Email</h3>
                  <a
                    href="mailto:blakejdanielson@gmail.com"
                    className="text-zinc-400 hover:text-purple-400 transition-colors"
                  >
                    blakejdanielson@gmail.com
                  </a>
                </div>
              </div>
            </Card>

            <Card className="border-zinc-800 bg-zinc-900/50 p-6 hover:border-purple-500/30 transition-colors">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-500/20 text-purple-400">
                  <Phone className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Phone</h3>
                  <a href="tel:9253249491" className="text-zinc-400 hover:text-purple-400 transition-colors">
                    (925) 324-9491
                  </a>
                </div>
              </div>
            </Card>

            <Card className="border-zinc-800 bg-zinc-900/50 p-6 hover:border-purple-500/30 transition-colors">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-500/20 text-purple-400">
                  <MapPin className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Location</h3>
                  <p className="text-zinc-400">Denver, CO</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Featured Music Player - UNCHANGED */}
      <div className="border-t border-zinc-800 bg-gradient-to-br from-zinc-900 to-purple-950/20 py-24">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-6xl">
            <div className="mb-12 text-center">
              <Badge className="mb-2 bg-purple-500/20 text-purple-300">Featured Tracks</Badge>
              <h2 className="text-3xl font-bold text-white">My Music</h2>
              <p className="mx-auto mt-4 max-w-2xl text-zinc-400">
                Music has been my creative outlet since I was 8. What started as a private passion has evolved into a
                serious side project—crafting bass-heavy beats that absolutely slap.
              </p>
            </div>

            <FeaturedMusicPlayer />

            <div className="mt-12 text-center">
              <Link href="/music">
                <Button className="bg-purple-600 hover:bg-purple-700">
                  Explore Full Music Portfolio
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Project Section - UNCHANGED */}
      <div className="border-t border-zinc-800 bg-black py-24">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-6xl">
            <div className="mb-12 text-center">
              <Badge className="mb-2 bg-purple-500/20 text-purple-300">Featured Project</Badge>
              <h2 className="text-3xl font-bold text-white">OurStories</h2>
              <p className="mx-auto mt-4 max-w-2xl text-zinc-400">
                A bedtime story generator that makes your child the star of the story, with AI-generated images and
                physical printing options.
              </p>
            </div>

            <div className="relative overflow-hidden rounded-xl border border-purple-500/20 bg-gradient-to-br from-zinc-900 to-black p-1">
              <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(0deg,#000000,transparent)]"></div>
              <div className="relative grid gap-8 p-6 md:grid-cols-2 md:p-10">
                <div className="flex flex-col justify-center space-y-4">
                  <Badge className="w-fit bg-purple-500/20 text-purple-300">AI</Badge>
                  <h2 className="text-3xl font-bold text-white">OurStories</h2>
                  <p className="text-zinc-400">
                    A bedtime story generator that makes your child the star of the story, with AI-generated images and
                    physical printing options. This passion project combines the magic of personalized storytelling with
                    cutting-edge AI to create unique, memorable experiences for families.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {["AI", "NLP", "Image Generation", "E-commerce"].map((tag) => (
                      <span key={tag} className="rounded-full bg-zinc-800 px-3 py-1 text-xs text-zinc-300">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="pt-4">
                    <Link href="/projects/ourstories">
                      <Button className="bg-purple-600 hover:bg-purple-700">
                        View Case Study
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
                <div className="relative aspect-video overflow-hidden rounded-lg border border-zinc-800">
                  <Image
                    src="/forest-friends-picnic.png"
                    alt="OurStories - AI Bedtime Story Generator"
                    fill
                    className="object-cover transition-transform duration-500 hover:scale-105"
                  />
                </div>
              </div>
            </div>

            <div className="mt-8 text-center">
              <Link href="/projects">
                <Button variant="outline" className="border-zinc-700 text-white hover:bg-zinc-800">
                  View All Projects
                  <ArrowRight className="ml-2 h-4 w-4" />
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
