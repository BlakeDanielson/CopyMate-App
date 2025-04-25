"use client"; // Add this at the top if not already present

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Image from "next/image";
import Link from "next/link";
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { CheckIcon } from "@radix-ui/react-icons";

// Placeholder icons (replace with actual icons if available)
const UploadIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" x2="12" y1="3" y2="15" />
  </svg>
);

const MessageSquareIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const DownloadIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" x2="12" y1="15" y2="3" />
  </svg>
);

// Placeholder icons (Features)
const EditIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4Z" />
  </svg>
);

const LayersIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 2 7 12 12 22 7 12 2" />
    <polyline points="2 17 12 22 22 17" />
    <polyline points="2 12 12 17 22 12" />
  </svg>
);

const SparklesIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.93 13.5a1.12 1.12 0 0 0-1.07 1.07 1.12 1.12 0 0 0 1.07 1.07 1.12 1.12 0 0 0 1.07-1.07zM14.07 13.5a1.12 1.12 0 0 0-1.07 1.07 1.12 1.12 0 0 0 1.07 1.07 1.12 1.12 0 0 0 1.07-1.07 1.12 1.12 0 0 0-1.07-1.07z"/>
    <path d="M12 2a1 1 0 0 0-1 1v2a1 1 0 0 0 2 0V3a1 1 0 0 0-1-1zM12 18a1 1 0 0 0-1 1v2a1 1 0 0 0 2 0v-2a1 1 0 0 0-1-1zM4.93 4.93a1 1 0 0 0-1.41 1.41L5.64 7.05a1 1 0 0 0 1.41-1.41zM16.95 16.95a1 1 0 0 0-1.41 1.41l2.12 2.12a1 1 0 0 0 1.41-1.41zM2 12a1 1 0 0 0 1 1h2a1 1 0 0 0 0-2H3a1 1 0 0 0-1 1zM18 12a1 1 0 0 0 1 1h2a1 1 0 0 0 0-2h-2a1 1 0 0 0-1 1zM7.05 16.95a1 1 0 0 0-1.41-1.41L4.93 19.07a1 1 0 0 0 1.41 1.41zM19.07 4.93a1 1 0 0 0-1.41-1.41L16.95 5.64a1 1 0 0 0 1.41 1.41z"/>
  </svg>
);

const ZapIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);

const UserCheckIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <polyline points="16 11 18 13 22 9" />
  </svg>
);

const CopyIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
  </svg>
);

const MessageCircleIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M7.9 20A9 9 0 1 0 4 12.1"/>
    <path d="M10 10v.01"/>
    <path d="M14 10v.01"/>
    <path d="M8 15h8"/>
    <path d="M18 16l-2.5-2.5"/>
    <path d="m6 16 2.5-2.5"/>
  </svg>
);

export default function Home() {
  return (
    <main className="flex-1">
      {/* Hero Section */}
      <section className="w-full pt-12 md:pt-24 lg:pt-32 bg-gradient-to-br from-purple-50 via-white to-pink-50">
        <div className="container mx-auto px-4 md:px-6 space-y-10 xl:space-y-16">
          <div className="grid max-w-[1300px] mx-auto gap-4 px-4 sm:px-6 md:px-10 md:grid-cols-2 md:gap-16">
            {/* Left Column: Text Content */}
            <div className="flex flex-col justify-center space-y-4">
              <div className="inline-block rounded-lg bg-purple-100 px-3 py-1 text-sm text-purple-800 font-medium">
                ✨ AI-Powered Photo Editing
              </div>
              <h1 className="lg:leading-tighter text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl xl:text-[3.4rem] 2xl:text-[3.75rem]">
                Chat with AI to Edit Your Product Photos
              </h1>
              <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                PixelChat AI transforms ordinary product images into professional, high-converting visuals through simple conversation. No design skills needed.
              </p>
              <div className="space-x-4 pt-4">
                <Button size="lg" asChild>
                  <Link href="#demo">Try Free Demo →</Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link href="#examples">See Examples</Link>
                </Button>
              </div>
              {/* How it works icons */}
              <div className="grid grid-cols-3 gap-4 pt-8 text-center">
                <div className="flex flex-col items-center space-y-2">
                  <UploadIcon className="h-8 w-8 text-purple-600" />
                  <span className="text-sm font-medium">Upload Photo</span>
                  <p className="text-xs text-gray-500">Upload any product image</p>
                </div>
                <div className="flex flex-col items-center space-y-2">
                  <MessageSquareIcon className="h-8 w-8 text-purple-600" />
                  <span className="text-sm font-medium">Chat with AI</span>
                  <p className="text-xs text-gray-500">Describe your desired edits</p>
                </div>
                <div className="flex flex-col items-center space-y-2">
                  <DownloadIcon className="h-8 w-8 text-purple-600" />
                  <span className="text-sm font-medium">Get Results</span>
                  <p className="text-xs text-gray-500">Download professional images</p>
                </div>
              </div>
            </div>

            {/* Right Column: Chat Interface Image */}
            <div className="flex items-center justify-center">
              <Image
                src="/chat-interface.jpg" // Make sure this image exists in /public
                alt="PixelChat AI Interface"
                width={1000} // Adjust as needed
                height={700} // Adjust as needed
                className="mx-auto aspect-[10/7] overflow-hidden rounded-xl object-cover shadow-xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="w-full py-12 md:py-24 lg:py-32 bg-white">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
              AI-Powered Conversational Editing
            </h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              Transform your product photos through simple conversation. No complex software or design skills required.
            </p>
          </div>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:gap-8">
            {[
              { icon: EditIcon, title: "Conversational Editing", description: "Edit photos through natural language chat. Simply describe what you want to change." },
              { icon: LayersIcon, title: "Background Removal", description: "Automatically remove backgrounds with a simple chat command." },
              { icon: SparklesIcon, title: "AI Enhancement", description: "Improve lighting, colors, and details with advanced AI models." },
              { icon: ZapIcon, title: "Instant Results", description: "Get professional-quality edits in seconds, not hours." },
              { icon: UserCheckIcon, title: "No Design Skills Needed", description: "Create professional product photos without any technical expertise." },
              { icon: CopyIcon, title: "Batch Processing", description: "Edit multiple product images with consistent quality through chat." },
            ].map((feature, index) => (
              <Card key={index} className="bg-gray-50/50 hover:bg-gray-100 transition-colors">
                <CardHeader className="flex flex-row items-center gap-4 pb-2">
                  <feature.icon className="h-8 w-8 text-purple-600" />
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="w-full py-12 md:py-24 lg:py-32 bg-gray-50/50">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
              How PixelChat AI Works
            </h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              Our AI-powered chatbot makes product photo editing as simple as having a conversation.
            </p>
          </div>

          {/* Step 1 */}
          <div className="mx-auto grid max-w-5xl items-center gap-6 lg:grid-cols-2 lg:gap-12 mb-16">
            <div className="flex flex-col justify-center space-y-4">
              <div className="inline-block rounded-lg bg-purple-100 px-3 py-1 text-sm text-purple-800 font-medium w-fit">Step 1</div>
              <h3 className="text-2xl font-bold tracking-tighter">Upload Your Product Photo</h3>
              <ul className="list-disc space-y-2 pl-5 text-gray-600">
                <li>Start by uploading any product image you want to enhance. Our system accepts all common image formats (JPG, PNG, WEBP) and automatically analyzes the content.</li>
                <li>Drag and drop or browse your files</li>
                <li>Automatic product detection</li>
                <li>Instant image analysis</li>
              </ul>
            </div>
            <Image
              src="/upload-interface.jpg" // Ensure this image exists
              alt="Upload Interface Example"
              width={550}
              height={310}
              className="mx-auto aspect-video overflow-hidden rounded-xl object-cover object-center sm:w-full lg:order-last shadow-lg border"
            />
          </div>

          {/* Step 2 */}
          <div className="mx-auto grid max-w-5xl items-center gap-6 lg:grid-cols-2 lg:gap-12 mb-16">
            <Image
              src="/chat-interface.jpg" // Reusing chat interface image, replace if a specific one exists
              alt="Chat Interface Example"
              width={550}
              height={310}
              className="mx-auto aspect-video overflow-hidden rounded-xl object-cover object-center sm:w-full shadow-lg border"
            />
            <div className="flex flex-col justify-center space-y-4">
              <div className="inline-block rounded-lg bg-purple-100 px-3 py-1 text-sm text-purple-800 font-medium w-fit">Step 2</div>
              <h3 className="text-2xl font-bold tracking-tighter">Chat With AI About Your Edits</h3>
              <ul className="list-disc space-y-2 pl-5 text-gray-600">
                <li>Simply tell our AI what changes you want in plain English. No technical jargon or complex instructions needed - just describe what you'd like to see.</li>
                <li>"Remove the background and make it white"</li>
                <li>"Brighten the product and make colors more vibrant"</li>
                <li>"Add a subtle shadow beneath the product"</li>
              </ul>
            </div>
          </div>

          {/* Step 3 */}
          <div className="mx-auto grid max-w-5xl items-center gap-6 lg:grid-cols-2 lg:gap-12">
            <div className="flex flex-col justify-center space-y-4">
              <div className="inline-block rounded-lg bg-purple-100 px-3 py-1 text-sm text-purple-800 font-medium w-fit">Step 3</div>
              <h3 className="text-2xl font-bold tracking-tighter">Get Professional Results Instantly</h3>
              <ul className="list-disc space-y-2 pl-5 text-gray-600">
                <li>Our AI applies your requested changes in seconds, delivering professional-quality results that would normally require hours of manual editing and expertise.</li>
                <li>Download in multiple formats and resolutions</li>
                <li>Request additional adjustments through chat</li>
                <li>Save editing history for future reference</li>
              </ul>
              <Link className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 w-fit mt-4"
                href="#workflow">
                See the full workflow in action →
              </Link>
            </div>
            <Image
              src="/results-interface.jpg" // Ensure this image exists
              alt="Results Interface Example"
              width={550}
              height={310}
              className="mx-auto aspect-video overflow-hidden rounded-xl object-cover object-center sm:w-full lg:order-last shadow-lg border"
            />
          </div>
        </div>
      </section>

      {/* Transformation Section */}
      <section id="transformation" className="w-full py-12 md:py-24 lg:py-32 bg-white">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
              See the Transformation
            </h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              Drag the slider to see how PixelChat AI transforms ordinary product photos into professional images.
            </p>
          </div>

          <Tabs defaultValue="jewelry" className="w-full max-w-5xl mx-auto">
            <TabsList className="grid w-full grid-cols-4 mb-8">
              <TabsTrigger value="jewelry">Jewelry</TabsTrigger>
              <TabsTrigger value="footwear">Footwear</TabsTrigger>
              <TabsTrigger value="electronics">Electronics</TabsTrigger>
              <TabsTrigger value="cosmetics">Cosmetics</TabsTrigger>
            </TabsList>
            {/* TODO: Add TabsContent for each category if dynamic images are needed */}
            {/* For now, just show one slider */} 
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
              {/* Slider Column */}
              <div className="md:col-span-2 rounded-xl overflow-hidden border shadow-lg">
                <ReactCompareSlider
                  itemOne={<ReactCompareSliderImage src="/product-before.jpg" alt="Image before" />}
                  itemTwo={<ReactCompareSliderImage src="/product-after.jpg" alt="Image after" />}
                  style={{ height: 'auto', width: '100%' }}
                />
              </div>

              {/* Explanation Column */}
              <div className="bg-gray-100 p-6 rounded-lg">
                 <div className="flex items-center gap-2 mb-4">
                    <MessageCircleIcon className="h-6 w-6 text-purple-600" />
                    <h4 className="text-sm font-semibold">Chat Prompt</h4>
                 </div>
                 <p className="text-sm text-gray-700 mb-6 bg-white p-4 rounded italic">
                   "Remove the background, add a subtle shadow, and make the gold more vibrant"
                 </p>

                 <h4 className="text-lg font-semibold mb-3">How This Works</h4>
                 <ul className="list-disc space-y-2 pl-5 text-sm text-gray-600">
                   <li>Simply describe what you want to change about your product photo in plain English.</li>
                   <li>Our AI understands your intent and applies professional editing techniques automatically.</li>
                   <li>No technical jargon needed</li>
                   <li>AI applies multiple edits from a single instruction</li>
                   <li>Refine results with follow-up requests</li>
                 </ul>
              </div>
            </div>
          </Tabs>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="w-full py-12 md:py-24 lg:py-32 bg-gray-50/50">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
              What Our Customers Say
            </h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              Businesses of all sizes are transforming their product photography with PixelChat AI.
            </p>
          </div>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:gap-8">
            {[
              {
                quote: "PixelChat AI has revolutionized our product photography workflow. We simply chat with the AI about what we want, and it delivers professional results in seconds.",
                name: "Sarah Johnson",
                title: "Modern Home Goods",
                avatar: "/placeholder-user.jpg", // Replace with actual image if available
              },
              {
                quote: "As an e-commerce manager handling hundreds of products, PixelChat AI has been a game-changer. The chat interface makes complex editing tasks incredibly simple.",
                name: "Michael Chen",
                title: "TechGear Direct",
                avatar: "/placeholder-user.jpg", // Replace with actual image if available
              },
              {
                quote: "The conversational approach to photo editing is brilliant. I just tell PixelChat what I want, and it understands exactly what I need for my product images.",
                name: "Emily Rodriguez",
                title: "Elegant Accessories",
                avatar: "/placeholder-user.jpg", // Replace with actual image if available
              },
            ].map((testimonial, index) => (
              <Card key={index} className="bg-white p-6 shadow-sm">
                <CardContent className="flex flex-col items-center text-center">
                  {/* Star Rating Placeholder */}
                  <div className="flex text-yellow-400 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <svg key={i} className="w-5 h-5 fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z"/></svg>
                    ))}
                  </div>
                  <p className="text-gray-600 italic mb-6">"{testimonial.quote}"</p>
                  <Avatar className="mb-2">
                    <AvatarImage src={testimonial.avatar} alt={testimonial.name} />
                    <AvatarFallback>{testimonial.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                  </Avatar>
                  <p className="font-semibold text-sm">{testimonial.name}</p>
                  <p className="text-xs text-gray-500">{testimonial.title}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          {/* TODO: Add "Joined by 2,500+ businesses" banner */}
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="w-full py-12 md:py-24 lg:py-32 bg-white">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">
              Simple, Transparent Pricing
            </h2>
            <p className="max-w-[900px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              Choose the perfect plan for your product photography needs.
            </p>
          </div>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:gap-8 items-start">
            {/* Starter Plan */}
            <Card className="flex flex-col p-6 bg-gray-50/50">
              <CardHeader className="pb-4">
                <CardTitle className="text-xl font-semibold">Starter</CardTitle>
                <CardDescription className="text-sm text-gray-500">Perfect for small businesses just getting started.</CardDescription>
                <div className="flex items-baseline gap-1 pt-4">
                  <span className="text-4xl font-bold">$29</span>
                  <span className="text-sm font-medium text-gray-500">/month</span>
                </div>
              </CardHeader>
              <CardContent className="flex-1 space-y-3">
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> 50 AI chat edits per month</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Background removal</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Basic enhancement</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Standard export quality</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Email support</li>
                </ul>
              </CardContent>
              <CardFooter className="mt-auto pt-4">
                <Button variant="outline" className="w-full">Get Started</Button>
              </CardFooter>
            </Card>

            {/* Professional Plan (Most Popular) */}
            <Card className="flex flex-col p-6 border-purple-500 border-2 relative shadow-lg">
              <div className="absolute top-0 -translate-y-1/2 left-1/2 -translate-x-1/2 bg-purple-600 text-white px-3 py-1 text-xs font-semibold rounded-full">
                Most Popular
              </div>
              <CardHeader className="pb-4">
                <CardTitle className="text-xl font-semibold">Professional</CardTitle>
                <CardDescription className="text-sm text-gray-500">For growing businesses with regular product updates.</CardDescription>
                <div className="flex items-baseline gap-1 pt-4">
                  <span className="text-4xl font-bold">$79</span>
                  <span className="text-sm font-medium text-gray-500">/month</span>
                </div>
              </CardHeader>
              <CardContent className="flex-1 space-y-3">
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-purple-600" /> 200 AI chat edits per month</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-purple-600" /> Advanced background removal</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-purple-600" /> Detail enhancement</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-purple-600" /> Shadow & reflection</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-purple-600" /> High-resolution exports</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-purple-600" /> Priority support</li>
                </ul>
              </CardContent>
              <CardFooter className="mt-auto pt-4">
                <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white">Go Pro</Button>
              </CardFooter>
            </Card>

            {/* Enterprise Plan */}
            <Card className="flex flex-col p-6 bg-gray-50/50">
              <CardHeader className="pb-4">
                <CardTitle className="text-xl font-semibold">Enterprise</CardTitle>
                <CardDescription className="text-sm text-gray-500">For large catalogs and e-commerce businesses.</CardDescription>
                <div className="flex items-baseline gap-1 pt-4">
                  <span className="text-4xl font-bold">Custom</span>
                </div>
              </CardHeader>
              <CardContent className="flex-1 space-y-3">
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Unlimited AI chat edits</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Custom workflows</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> API access</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Batch processing</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Ultra HD exports</li>
                  <li className="flex items-center gap-2"><CheckIcon className="h-4 w-4 text-green-500" /> Dedicated account manager</li>
                </ul>
              </CardContent>
              <CardFooter className="mt-auto pt-4">
                <Button variant="outline" className="w-full">Contact Sales</Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="cta" className="w-full py-12 md:py-24 lg:py-32 bg-gray-100 dark:bg-gray-800">
        <div className="container grid items-center justify-center gap-4 px-4 text-center md:px-6">
          <div className="space-y-3">
            <h2 className="text-3xl font-bold tracking-tighter md:text-4xl/tight">
              Ready to Transform Your Product Photos?
            </h2>
            <p className="mx-auto max-w-[600px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              Join thousands of businesses already using PixelChat AI to create professional product images through simple conversation.
            </p>
          </div>
          <div className="flex flex-col gap-2 min-[400px]:flex-row justify-center">
            <Button size="lg" asChild>
              <Link href="#">Start Free Trial</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="#demo">See Demo →</Link>
            </Button>
          </div>
           <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">No credit card required. 14-day free trial.</p>
        </div>
      </section>

      {/* Footer Placeholder - Will be replaced by Footer component later */}
      {/* <div className="flex-grow container mx-auto px-4 py-16">
        <h2 className="text-xl font-semibold text-center text-gray-500">Footer coming soon...</h2>
      </div> */}
    </main>
  );
}
