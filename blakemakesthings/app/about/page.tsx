import Image from "next/image"
import Link from "next/link"
import { ArrowRight, Heart, Sparkles } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"
import { AnimatedText } from "@/components/animated-text"

export default function AboutPage() {
  // Identity/role phrases for animation
  const identityPhrases = [
    "product manager",
    "entrepreneur",
    "consultant",
    "music producer",
    "finance professional",
    "strategic advisor",
    "database wizard",
  ]

  return (
    <div className="min-h-screen bg-black">
      <MainNav />

      {/* Header Section */}
      <div className="relative bg-zinc-900 pt-24">
        <div className="absolute inset-0 bg-grid-white/5 opacity-50"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 to-zinc-900"></div>

        <div className="container relative z-10 mx-auto px-4 py-16 text-center">
          <Badge className="mb-4 bg-purple-500/20 text-purple-300">Finance Professional & Product Manager</Badge>
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl">
            About <span className="text-purple-400">Me</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-zinc-300">
            From financial analysis to product management, with a side of bass music and motorcycles
          </p>

          <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-black to-transparent"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-6xl">
          {/* Bio Section */}
          <div className="relative rounded-xl border border-purple-500/20 bg-gradient-to-br from-zinc-900 to-black p-1">
            <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(0deg,#000000,transparent)]"></div>
            <div className="relative grid gap-8 p-6 md:grid-cols-2 md:p-10">
              <div className="flex flex-col justify-center space-y-6">
                <div className="inline-flex items-center rounded-full bg-purple-500/10 px-3 py-1 text-sm text-purple-300">
                  <Sparkles className="mr-2 h-4 w-4" />
                  <span>Blake Danielson</span>
                </div>

                <h2 className="text-2xl font-bold text-white text-animation-container sm:text-3xl">
                  <span className="flex flex-wrap items-center whitespace-nowrap">
                    <span className="whitespace-nowrap">Hi, I'm Blake, I'm a&nbsp;</span>
                    <AnimatedText phrases={identityPhrases} highlightClassName="text-purple-400" inline={true} />
                  </span>
                </h2>

                <div className="space-y-4 text-zinc-400">
                  <p>
                    I started my academic journey in computer science, but quickly realized my true strength lies not
                    just in coding, but in bridging people, technology, and business. I transitioned to a finance major
                    at the University of Denver, initially pursuing investment banking. After securing a highly
                    competitive internship meant for seniors during my junior year—and experiencing the intense grind
                    firsthand—I decided to pivot toward something more personally fulfilling.
                  </p>

                  <p>
                    I found an early stride in college with entrepreneurial ventures and emerging markets. Alongside
                    close friends, I founded a cryptocurrency arbitrage group, capitalizing on pricing inefficiencies
                    across crypto exchanges.
                  </p>

                  <p>
                    Concurrently, I wrote analytical articles about cannabis stocks during Canada's booming "green
                    rush," contributing content to platforms like Seeking Alpha under the handle "DeltaBot Capital". My
                    passion for this emerging industry led to additional writing opportunities for Mesh Media Group,
                    where I authored their "Marijuana Investing Report" and "The Next Big Profit" weekly newsletters—
                    publications that grew to over $100k in subscriptions during their first year.
                  </p>

                  <p>
                    This unique path caught the attention of Snoop Dogg's venture capital fund, Casa Verde Capital,
                    where I contributed remotely throughout my senior year. Post-graduation, my professional journey has
                    included:
                  </p>

                  <ul className="list-disc pl-5 space-y-2">
                    <li>Working as a direct report for the CEO of the largest legal cannabis operator in California</li>
                    <li>Helping to deploy $80 million in the cannabis sector</li>
                    <li>Leading analysis and financial modeling used to pitch and land Fortune 50 companies</li>
                    <li>Developing executive dashboards that transformed strategic decision-making processes</li>
                  </ul>

                  <p>
                    I pride myself on blending financial acumen with product-driven thinking, turning complex data into
                    actionable insights—saving businesses substantial amounts through workflow automation and
                    streamlined database systems.
                  </p>

                  <p>
                    Outside of work, you can always catch me somewhere with loud music. I've been producing EDM and
                    hip-hop beats in my bedroom for years and proudly attended 11 Red Rocks shows in 2024—a feat I would
                    argue should garner the same respect as a sizeable professional accomplishment.
                  </p>
                </div>

                <div className="flex flex-wrap gap-3">
                  <Link href="/projects">
                    <Button className="bg-purple-600 hover:bg-purple-700">
                      View My Work
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                  <Link href="/contact">
                    <Button variant="outline" className="border-zinc-700 text-white hover:bg-zinc-800">
                      Get in Touch
                    </Button>
                  </Link>
                  {/* Social media links */}
                  <div className="flex space-x-4">
                    <Link
                      href="https://www.linkedin.com/in/blakedan97/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="rounded-full bg-zinc-800 p-3 text-zinc-400 transition-colors hover:bg-purple-500/20 hover:text-purple-300"
                    >
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path
                          fillRule="evenodd"
                          d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </Link>
                    <Link
                      href="https://github.com/BlakeDanielson"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="rounded-full bg-zinc-800 p-3 text-zinc-400 transition-colors hover:bg-purple-500/20 hover:text-purple-300"
                    >
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path
                          fillRule="evenodd"
                          d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </Link>
                    <Link
                      href="https://soundcloud.com/blvkemusic"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="rounded-full bg-zinc-800 p-3 text-zinc-400 transition-colors hover:bg-purple-500/20 hover:text-purple-300"
                    >
                      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M11.56 8.87V17h1.01V8.87c0-.28-.22-.5-.5-.5s-.51.23-.51.5zM8.46 12v5h1.01v-5c0-.28-.22-.5-.5-.5s-.51.22-.51.5zM5.33 12v5h1.01v-5c0-.28-.22-.5-.5s-.51.22-.51.5zM2.24 12.87v4.13h1.01v-4.13c0-.28-.23-.5-.51-.5-.27 0-.5.22-.5.5zM0 14.5v2.5h1.01v-2.5c0-.28-.23-.5-.51-.5-.27 0-.5.22-.5.5zM19.83 8.6c-.28 0-.5.22-.5.5v7.9h1.01v-7.9c0-.28-.23-.5-.51-.5zM16.72 7.22c-.28 0-.5.22-.5V17h1.01V7.72c0-.28-.23-.5-.51-.5zM13.62 8.87V17h1.01V8.87c0-.28-.22-.5-.5-.5s-.51.23-.51.5zM22.92 9.6c-.28 0-.5.22-.5.5v6.9h1.01v-6.9c0-.28-.23-.5-.51-.5z" />
                      </svg>
                    </Link>
                  </div>
                </div>
              </div>

              <div className="relative">
                <div className="absolute -left-6 -top-6 h-24 w-24 rounded-full bg-purple-500/20 blur-2xl"></div>
                <div className="relative aspect-[3/4] overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900">
                  <Image src="/blake.jpg" alt="Blake Danielson" fill className="object-cover" />
                </div>
                <div className="absolute -bottom-4 -right-4 rounded-lg border border-zinc-800 bg-zinc-900/90 p-4 shadow-lg">
                  <div className="flex items-center gap-3">
                    <Heart className="h-5 w-5 text-purple-500" />
                    <span className="text-sm font-medium text-white">Future business owner in the making</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Professional Journey */}
          <div className="mt-24">
            <div className="mb-12 text-center">
              <Badge className="mb-2 bg-purple-500/20 text-purple-300">Experience</Badge>
              <h2 className="text-3xl font-bold text-white">Professional Journey</h2>
              <p className="mx-auto mt-4 max-w-2xl text-zinc-400">
                My path through finance, business development, and product management
              </p>
            </div>

            {/* Horizontal Timeline for Desktop */}
            <div className="relative hidden md:block">
              {/* Timeline line */}
              <div className="absolute left-0 right-0 top-16 h-0.5 bg-gradient-to-r from-purple-500/50 via-purple-500/30 to-zinc-800"></div>

              {/* Timeline items */}
              <div className="relative mx-auto max-w-6xl">
                <div className="grid grid-cols-3 gap-6">
                  {/* Item 1 - Present */}
                  <div className="relative">
                    <div className="absolute left-1/2 top-16 -ml-3 h-6 w-6 -translate-y-1/2 transform">
                      <div className="flex h-6 w-6 items-center justify-center rounded-full border border-purple-500/30 bg-zinc-900 shadow-lg shadow-purple-500/10">
                        <div className="h-2 w-2 rounded-full bg-purple-500"></div>
                      </div>
                    </div>

                    <div className="pt-24">
                      <span className="inline-block rounded-full bg-purple-500/10 px-3 py-1 text-xs text-purple-300">
                        Present
                      </span>
                      <h3 className="mt-2 text-xl font-bold text-white">Director of Sales</h3>
                      <p className="mt-1 text-zinc-400">Stealth Startup</p>
                      <p className="mt-4 text-zinc-400">
                        Building SaaS tools for the home service industry. Managing SQL databases, designing automation
                        systems, and integrating data from multiple sources to create unified platforms.
                      </p>
                      <div className="mt-4 flex flex-wrap gap-2">
                        <Badge variant="outline" className="border-zinc-700">
                          SQL
                        </Badge>
                        <Badge variant="outline" className="border-zinc-700">
                          Automation
                        </Badge>
                        <Badge variant="outline" className="border-zinc-700">
                          Data Integration
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Item 2 */}
                  <div className="relative">
                    <div className="absolute left-1/2 top-16 -ml-3 h-6 w-6 -translate-y-1/2 transform">
                      <div className="flex h-6 w-6 items-center justify-center rounded-full border border-purple-500/30 bg-zinc-900 shadow-lg shadow-purple-500/10">
                        <div className="h-2 w-2 rounded-full bg-purple-500"></div>
                      </div>
                    </div>

                    <div className="pt-24">
                      <span className="inline-block rounded-full bg-purple-500/10 px-3 py-1 text-xs text-purple-300">
                        Previous
                      </span>
                      <h3 className="mt-2 text-xl font-bold text-white">Director of Research and Analysis</h3>
                      <p className="mt-1 text-zinc-400">Dalton Capital</p>
                      <p className="mt-4 text-zinc-400">
                        Led operational efficiency initiatives saving $100K+ annually, built financial models for
                        Fortune 100 executives, and directed research on emerging technologies like AI to inform company
                        strategy.
                      </p>
                      <div className="mt-4 flex flex-wrap gap-2">
                        <Badge variant="outline" className="border-zinc-700">
                          Financial Modeling
                        </Badge>
                        <Badge variant="outline" className="border-zinc-700">
                          Process Optimization
                        </Badge>
                        <Badge variant="outline" className="border-zinc-700">
                          Product Development
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Item 3 */}
                  <div className="relative">
                    <div className="absolute left-1/2 top-16 -ml-3 h-6 w-6 -translate-y-1/2 transform">
                      <div className="flex h-6 w-6 items-center justify-center rounded-full border border-purple-500/30 bg-zinc-900 shadow-lg shadow-purple-500/10">
                        <div className="h-2 w-2 rounded-full bg-purple-500"></div>
                      </div>
                    </div>

                    <div className="pt-24">
                      <span className="inline-block rounded-full bg-purple-500/10 px-3 py-1 text-xs text-purple-300">
                        Previous
                      </span>
                      <h3 className="mt-2 text-xl font-bold text-white">Special Projects Manager</h3>
                      <p className="mt-1 text-zinc-400">Vertical Companies</p>
                      <p className="mt-4 text-zinc-400">
                        Partnered with executive leadership to secure $80M in fundraising, led M&A due diligence for
                        dispensary acquisitions, and built executive dashboards that centralized real-time data across
                        operations.
                      </p>
                      <div className="mt-4 flex flex-wrap gap-2">
                        <Badge variant="outline" className="border-zinc-700">
                          Fundraising
                        </Badge>
                        <Badge variant="outline" className="border-zinc-700">
                          M&A
                        </Badge>
                        <Badge variant="outline" className="border-zinc-700">
                          Cannabis Industry
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Music Section */}
            <div className="mt-24">
              <div className="mb-12 text-center">
                <Badge className="mb-2 bg-purple-500/20 text-purple-300">Passion Project</Badge>
                <h2 className="text-3xl font-bold text-white">Music Production</h2>
                <p className="mx-auto mt-4 max-w-2xl text-zinc-400">
                  I don't understand what Genres are, I like making sounds that sound cool
                </p>
              </div>

              <div className="grid gap-8 md:grid-cols-2">
                <div className="relative overflow-hidden rounded-xl border border-zinc-800">
                  <Image
                    src="/professional-music-studio.png"
                    alt="Music Production Setup"
                    width={600}
                    height={400}
                    className="w-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
                  <div className="absolute bottom-0 left-0 right-0 p-6">
                    <h3 className="text-xl font-bold text-white">The Studio</h3>
                    <p className="mt-2 text-zinc-300">Where the magic happens</p>
                  </div>
                </div>

                <div className="space-y-6">
                  <p className="text-zinc-400">
                    Music production has been my creative outlet for since I started learning guitar when I was 8.
                    Unlike my other pursuits, this one has always been purely for the love of it, and wasn't something I
                    ever shared publically until quite recently.
                  </p>
                  <p className="text-zinc-400">
                    I specialize in bass music, EDM, and hip hop beats that absolutely slap. You can find my tracks on
                    YouTube, SoundCloud, Instagram, TikTok, and I sell beats on BeatStars and Traktrain.
                  </p>
                  <p className="text-zinc-400">
                    When I'm not producing, I'm out experiencing live music at Denver venues. I'm either going wild
                    dancing in the pit or the nerd against the wall taking notes on production techniques I want to try
                    out. Either way, I'm soaking up inspiration from artists at the top of their game.
                  </p>
                  <div className="pt-4">
                    <Link href="/music">
                      <Button className="bg-purple-600 hover:bg-purple-700">
                        Explore My Music
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            {/* Future Goals */}
            <div className="mt-24">
              <div className="mb-12 text-center">
                <Badge className="mb-2 bg-purple-500/20 text-purple-300">The Future</Badge>
                <h2 className="text-3xl font-bold text-white">Where I'm Headed</h2>
                <p className="mx-auto mt-4 max-w-2xl text-zinc-400">My vision for the next chapter</p>
              </div>

              <div className="relative rounded-xl border border-purple-500/20 bg-gradient-to-br from-zinc-900 to-black p-8">
                <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(0deg,#000000,transparent)]"></div>
                <div className="relative">
                  <p className="text-lg text-zinc-300">
                    I'm seeking a long-term opportunity with a forward-thinking company that's making a significant
                    impact not just in its industry but the world as well. My goal is to find an organization where I
                    can grow alongside the business, becoming deeply invested in its vision and success.
                  </p>
                  <p className="mt-4 text-lg text-zinc-300">
                    My default is to view every challenge through an owner's lens — which made school just such a blast
                    growing up, but is an innate part of how my mind works. Where others might see isolated tasks, I
                    instinctively grasp the strategic implications and quickly connect the dots to the impact on both
                    the organization and the actual people whos buy-in and genuine support is essential to any success.
                    This perspective allows me to align seamlessly with executive vision in ways most employees struggle
                    to achieve. I've consistently found that my ability to understand business objectives at the highest
                    level transforms me into a uniquely valuable asset, particularly in environments where I can
                    leverage this perspective by interacting with those in leadership roles to help steer the
                    organization toward its most ambitious goals.
                  </p>
                  <p className="mt-4 text-lg text-zinc-300">
                    Rather than just filling a role, I'm looking to build a lasting career where I can apply my unique
                    blend of financial expertise and product-driven thinking to create substantial value. The ideal
                    company for me is one that values innovation, embraces change, and provides the space for motivated
                    individuals to make a meaningful difference.
                  </p>
                  <div className="mt-8">
                    <Link href="/contact">
                      <Button className="bg-purple-600 hover:bg-purple-700">
                        Let's Connect
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <SiteFooter />
    </div>
  )
}
