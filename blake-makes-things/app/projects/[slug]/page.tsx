import Image from "next/image"
import Link from "next/link"
import { notFound } from "next/navigation"
import { ArrowLeft, ExternalLink, Github, Calendar, Users, Sparkles } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MainNav } from "@/components/main-nav"
import { SiteFooter } from "@/components/site-footer"

interface ProjectPageProps {
  params: {
    slug: string
  }
}

// This would typically come from a database or CMS
const projects = {
  "ai-content-generator": {
    title: "AI Content Generator",
    description: "Helping creative teams break through writer's block with AI that understands their unique voice.",
    objective:
      "To create a tool that helps marketing teams generate high-quality content quickly and efficiently, reducing the time and resources required for content creation while maintaining their authentic voice.",
    role: "Lead Product Manager & AI Developer",
    duration: "6 months",
    team: "5 people",
    technologies: ["OpenAI GPT-4", "React", "Next.js", "Node.js", "MongoDB"],
    outcomes: [
      "Reduced content creation time by 70%",
      "Increased marketing team productivity by 45%",
      "Generated over 10,000 pieces of content in the first month",
      "Achieved 95% user satisfaction rating",
    ],
    story:
      "This project was born from my own frustration as a writer. I noticed how much time creative teams spent staring at blank pages, and wondered if AI could help spark ideas while preserving their unique voice. The journey wasn't straightforward - early versions felt too robotic and generic. The breakthrough came when we shifted from trying to replace human creativity to enhancing it, creating a collaborative tool that feels like a thoughtful partner rather than an automated replacement.",
    image: "/placeholder.svg?height=600&width=1200",
    gallery: [
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
    ],
    demoUrl: "https://example.com",
    githubUrl: "https://github.com",
    testimonial: {
      quote:
        "This tool has completely transformed our content creation process. It feels like having a brilliant collaborator who never gets tired and always has fresh ideas.",
      author: "Sarah Johnson",
      role: "Content Director, CreativeHub",
    },
    category: "Natural Language Processing",
  },
  "predictive-analytics": {
    title: "Predictive Analytics Dashboard",
    description: "Turning complex data into intuitive insights that anyone can understand and act on.",
    objective:
      "To develop a predictive analytics dashboard that helps businesses anticipate market trends, customer behavior, and potential risks, enabling proactive decision-making without requiring data science expertise.",
    role: "Product Manager & Data Scientist",
    duration: "8 months",
    team: "7 people",
    technologies: ["Python", "TensorFlow", "React", "D3.js", "AWS"],
    outcomes: [
      "Improved forecast accuracy by 35%",
      "Reduced operational costs by 25%",
      "Enabled early risk detection, preventing $2M in potential losses",
      "Adopted by 15 enterprise clients within first quarter",
    ],
    story:
      "This project started with a simple observation: most data dashboards are built for analysts, not decision-makers. I wanted to create something that would translate complex patterns into actionable insights for people without technical backgrounds. The biggest challenge was finding the right balance between simplicity and depth - we needed to make the interface intuitive without oversimplifying the underlying complexity of the data. The solution came through extensive user testing with actual business leaders, focusing on their decision-making process rather than just data visualization.",
    image: "/placeholder.svg?height=600&width=1200",
    gallery: [
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
    ],
    demoUrl: "https://example.com",
    githubUrl: "https://github.com",
    testimonial: {
      quote:
        "For the first time, I feel like I can actually see the future of our business. The insights are presented so clearly that making decisions feels almost intuitive.",
      author: "Michael Chen",
      role: "COO, TechInnovate",
    },
    category: "Data Visualization",
  },
  "conversational-ai": {
    title: "Conversational AI Assistant",
    description: "A friendly AI companion that makes technology more accessible through natural conversation.",
    objective:
      "To create an intuitive conversational AI assistant that understands natural language queries and helps users find information and complete tasks efficiently, with a focus on accessibility and natural interaction.",
    role: "Product Owner & NLP Engineer",
    duration: "10 months",
    team: "6 people",
    technologies: ["BERT", "PyTorch", "React", "Node.js", "Redis"],
    outcomes: [
      "Reduced customer support inquiries by 40%",
      "Achieved 85% query resolution rate",
      "Processed over 50,000 conversations in first month",
      "Decreased average resolution time from 15 minutes to 2 minutes",
    ],
    story:
      "This project was inspired by my grandmother, who struggled with technology but loved to talk. I wondered if we could create an interface that felt more like a conversation with a helpful friend than interacting with a computer. The development process involved countless hours of listening to how people naturally ask questions and express needs. We discovered that personality and empathy were just as important as technical accuracy - users forgave minor errors if the assistant felt genuinely helpful and responsive to their emotional state.",
    image: "/placeholder.svg?height=600&width=1200",
    gallery: [
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
    ],
    demoUrl: "https://example.com",
    githubUrl: "https://github.com",
    testimonial: {
      quote:
        "Your assistant has changed how I interact with technology. It's like having a patient friend who's always there to help me navigate the digital world.",
      author: "Eleanor Rivera",
      role: "Retired Teacher",
    },
    category: "Conversational AI",
  },
  "computer-vision": {
    title: "Computer Vision Product Classifier",
    description: "Teaching computers to see products the way humans do, making visual search intuitive and accurate.",
    objective:
      "To develop a computer vision system that automatically categorizes products based on visual characteristics, streamlining inventory management and improving search functionality.",
    role: "Technical Product Manager",
    duration: "7 months",
    team: "4 people",
    technologies: ["PyTorch", "OpenCV", "TensorFlow", "AWS SageMaker", "React"],
    outcomes: [
      "Achieved 97% classification accuracy",
      "Reduced manual categorization time by 90%",
      "Processed 100,000+ product images in first week",
      "Improved search relevance by 65%",
    ],
    story:
      "This project began with a simple question: why can't we search for products the way we naturally describe them? The journey took us deep into how humans perceive and categorize visual information, and how to translate that into algorithms that could 'see' in a similar way. One of the most fascinating challenges was teaching the system to understand context and cultural nuances in how products are presented and perceived.",
    image: "/placeholder.svg?height=600&width=1200",
    gallery: [
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
    ],
    demoUrl: "https://example.com",
    githubUrl: "https://github.com",
    testimonial: {
      quote:
        "The visual search capability has transformed our e-commerce platform. Customers can now find exactly what they're looking for without having to know the exact terminology.",
      author: "Priya Patel",
      role: "Digital Experience Director, StyleHouse",
    },
    category: "Computer Vision",
  },
  "recommendation-engine": {
    title: "Recommendation Engine",
    description: "Discovering the perfect match between people and products through the magic of AI.",
    objective:
      "To build a sophisticated recommendation engine that analyzes user behavior and preferences to provide personalized product suggestions, enhancing user experience and increasing conversion rates.",
    role: "Product Manager & ML Engineer",
    duration: "9 months",
    team: "5 people",
    technologies: ["Python", "Collaborative Filtering", "Matrix Factorization", "React", "PostgreSQL"],
    outcomes: [
      "Increased conversion rate by 28%",
      "Improved average order value by 15%",
      "Reduced bounce rate by 35%",
      "Generated $1.2M in additional revenue in first quarter",
    ],
    story:
      "This project was inspired by the joy of discovery - that moment when someone introduces you to something you didn't know you'd love. We wanted to recreate that feeling at scale. The technical challenge was balancing personalization with exploration - recommending items users would likely enjoy while still introducing them to new possibilities they might not have discovered on their own. The breakthrough came when we started thinking of the system less as a prediction engine and more as a thoughtful curator with a deep understanding of both products and people.",
    image: "/placeholder.svg?height=600&width=1200",
    gallery: [
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
    ],
    demoUrl: "https://example.com",
    githubUrl: "https://github.com",
    testimonial: {
      quote:
        "Your recommendation engine doesn't just suggest products - it feels like it actually understands my taste. I've discovered so many items I now love that I would never have found on my own.",
      author: "Thomas Wright",
      role: "Loyal Customer",
    },
    category: "Machine Learning",
  },
  "sentiment-analysis": {
    title: "Sentiment Analysis Tool",
    description: "Listening to the emotional heartbeat of customer feedback to create better experiences.",
    objective:
      "To create a sentiment analysis tool that processes customer feedback from multiple channels, identifying sentiment trends and key themes to inform product development and customer service improvements.",
    role: "Product Lead & NLP Specialist",
    duration: "5 months",
    team: "3 people",
    technologies: ["NLTK", "spaCy", "React", "Node.js", "MongoDB"],
    outcomes: [
      "Identified 15 critical product improvement opportunities",
      "Improved customer satisfaction score by 18%",
      "Reduced negative feedback by 30%",
      "Processed 50,000+ customer comments across 5 channels",
    ],
    story:
      "This project began with a simple observation: companies collect mountains of feedback but struggle to extract meaningful insights from it. The challenge wasn't just technical - it was about understanding the nuances of human expression. Sarcasm, cultural references, and evolving slang all presented fascinating puzzles to solve. We approached the problem by combining linguistic expertise with machine learning, creating a system that could detect not just positive or negative sentiment, but the specific emotions and concerns behind customer comments.",
    image: "/placeholder.svg?height=600&width=1200",
    gallery: [
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
      "/placeholder.svg?height=400&width=600",
    ],
    demoUrl: "https://example.com",
    githubUrl: "https://github.com",
    testimonial: {
      quote:
        "For the first time, we truly understand what our customers are feeling, not just what they're saying. This has transformed how we approach product development and customer service.",
      author: "Jasmine Lee",
      role: "Customer Experience Director, ServiceFirst",
    },
    category: "Natural Language Processing",
  },
}

export default function ProjectPage({ params }: ProjectPageProps) {
  const project = projects[params.slug as keyof typeof projects]

  if (!project) {
    notFound()
  }

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
            <Badge className="mb-4 bg-purple-500/20 text-purple-300">{project.category}</Badge>
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">{project.title}</h1>
            <p className="mt-4 text-xl text-zinc-400">{project.description}</p>
          </div>

          <div className="mt-8 overflow-hidden rounded-xl border border-zinc-800">
            <Image
              src={project.image || "/placeholder.svg"}
              alt={project.title}
              width={1200}
              height={600}
              className="w-full object-cover"
            />
          </div>

          <div className="mt-12 grid gap-12 md:grid-cols-3">
            <div className="space-y-6 md:col-span-2">
              <div>
                <h2 className="text-2xl font-bold text-white">The Challenge</h2>
                <p className="mt-4 text-zinc-400">{project.objective}</p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">The Story</h2>
                <p className="mt-4 text-zinc-400">{project.story}</p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-white">Outcomes</h2>
                <ul className="mt-4 space-y-2 text-zinc-400">
                  {project.outcomes.map((outcome, index) => (
                    <li key={index} className="flex items-start">
                      <Sparkles className="mr-2 mt-1 h-4 w-4 flex-shrink-0 text-purple-500" />
                      <span>{outcome}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {project.gallery.map((image, index) => (
                  <div key={index} className="overflow-hidden rounded-lg border border-zinc-800">
                    <Image
                      src={image || "/placeholder.svg"}
                      alt={`${project.title} screenshot ${index + 1}`}
                      width={400}
                      height={300}
                      className="aspect-[4/3] w-full object-cover"
                    />
                  </div>
                ))}
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
                      <p className="font-medium text-white">{project.role}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">Duration</p>
                      <p className="font-medium text-white">{project.duration}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-zinc-500">Team Size</p>
                      <p className="font-medium text-white">{project.team}</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <p className="text-sm text-zinc-500">Technologies</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {project.technologies.map((tech) => (
                      <Badge key={tech} variant="outline" className="border-zinc-700">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="mt-6 flex flex-col gap-3">
                  <Link href={project.demoUrl} target="_blank" rel="noopener noreferrer">
                    <Button className="w-full bg-purple-600 hover:bg-purple-700">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      View Live Demo
                    </Button>
                  </Link>
                  <Link href={project.githubUrl} target="_blank" rel="noopener noreferrer">
                    <Button variant="outline" className="w-full border-zinc-700">
                      <Github className="mr-2 h-4 w-4" />
                      View Source Code
                    </Button>
                  </Link>
                </div>
              </div>

              {project.testimonial && (
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
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
                  <p className="mt-4 italic text-zinc-400">"{project.testimonial.quote}"</p>
                  <div className="mt-4">
                    <p className="font-medium text-white">{project.testimonial.author}</p>
                    <p className="text-sm text-zinc-500">{project.testimonial.role}</p>
                  </div>
                </div>
              )}
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
