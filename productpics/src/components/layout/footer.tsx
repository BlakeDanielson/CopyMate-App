"use client";

import Link from 'next/link';
import Image from 'next/image';

// Placeholder Social Icons
const FacebookIcon = (props: React.SVGProps<SVGSVGElement>) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" />
    </svg>
);

const TwitterIcon = (props: React.SVGProps<SVGSVGElement>) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 4s-.7 2.1-2 3.4c1.6 1.4 3.6 3.6 3.6 3.6s-1.6-1.4-3.6-1.4c-2 0-4.4 2.4-4.4 2.4s-.4-1.4-2-3.4c-1.6-2-4.4-3.6-4.4-3.6s2.8.4 4.4 2.4c1.6 2 2.4 4.4 2.4 4.4s-1.8-.8-3.4-2.2c-1.6-1.4-3.4-3.4-3.4-3.4s1.8.8 3.4 2.2c1.6 1.4 3.4 3.4 3.4 3.4s-4-4.8-10.4-6.8" />
    </svg>
);

const InstagramIcon = (props: React.SVGProps<SVGSVGElement>) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect width="20" height="20" x="2" y="2" rx="5" ry="5" />
        <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
        <line x1="17.5" x2="17.51" y1="6.5" y2="6.5" />
    </svg>
);

const LinkedinIcon = (props: React.SVGProps<SVGSVGElement>) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
        <rect width="4" height="12" x="2" y="9" />
        <circle cx="4" cy="4" r="2" />
    </svg>
);

export function Footer() {
  return (
    <footer className="border-t">
      <div className="container mx-auto px-4 py-8 md:py-12">
        <div className="grid gap-10 row-gap-6 mb-8 sm:grid-cols-2 lg:grid-cols-4">
          <div className="sm:col-span-2">
            <Link href="/" className="inline-flex items-center">
              <Image src="/placeholder-logo.svg" alt="PixelChat Logo" width={32} height={32} className="mr-2"/>
              <span className="text-xl font-bold tracking-wide text-gray-800 uppercase">
                PixelChat AI
              </span>
            </Link>
            <div className="mt-6 lg:max-w-sm">
              <p className="text-sm text-gray-600">
                Transform your product photos through simple conversation with our AI-powered editing assistant.
              </p>
            </div>
          </div>
          <div className="space-y-2 text-sm">
            <p className="text-base font-bold tracking-wide text-gray-900">Product</p>
            <div className="flex flex-col space-y-2">
              <Link href="#features" className="text-gray-600 transition-colors duration-300 hover:text-deep-purple-accent-400">Features</Link>
              <Link href="#how-it-works" className="text-gray-600 transition-colors duration-300 hover:text-deep-purple-accent-400">How it Works</Link>
              <Link href="#pricing" className="text-gray-600 transition-colors duration-300 hover:text-deep-purple-accent-400">Pricing</Link>
              <Link href="#" className="text-gray-600 transition-colors duration-300 hover:text-deep-purple-accent-400">API</Link>
            </div>
          </div>
          <div className="space-y-2 text-sm">
            <p className="text-base font-bold tracking-wide text-gray-900">Company</p>
            <div className="flex flex-col space-y-2">
              <Link href="#" className="text-gray-600 transition-colors duration-300 hover:text-deep-purple-accent-400">About Us</Link>
              <Link href="#" className="text-gray-600 transition-colors duration-300 hover:text-deep-purple-accent-400">Blog</Link>
              <Link href="#" className="text-gray-600 transition-colors duration-300 hover:text-deep-purple-accent-400">Contact</Link>
            </div>
            <p className="text-base font-bold tracking-wide text-gray-900 mt-4">Connect</p>
             <div className="flex items-center mt-1 space-x-3">
                <Link href="#" className="text-gray-500 transition-colors duration-300 hover:text-deep-purple-accent-400"><FacebookIcon className="h-5 w-5"/></Link>
                <Link href="#" className="text-gray-500 transition-colors duration-300 hover:text-deep-purple-accent-400"><TwitterIcon className="h-5 w-5"/></Link>
                <Link href="#" className="text-gray-500 transition-colors duration-300 hover:text-deep-purple-accent-400"><InstagramIcon className="h-5 w-5"/></Link>
                <Link href="#" className="text-gray-500 transition-colors duration-300 hover:text-deep-purple-accent-400"><LinkedinIcon className="h-5 w-5"/></Link>
            </div>
            <a href="mailto:hello@pixelchat.ai" className="text-gray-600 transition-colors duration-300 hover:text-deep-purple-accent-400 text-sm">hello@pixelchat.ai</a>
          </div>
        </div>
        <div className="flex flex-col-reverse justify-between pt-5 pb-10 border-t lg:flex-row">
          <p className="text-sm text-gray-600">
            © 2025 PixelChat AI. All rights reserved.
          </p>
          {/* Optional: Add terms/privacy links here */}
        </div>
      </div>
    </footer>
  );
} 