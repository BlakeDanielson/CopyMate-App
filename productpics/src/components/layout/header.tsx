"use client";

import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { HamburgerMenuIcon } from '@radix-ui/react-icons'; // Or another menu icon
import { useState } from 'react';
import { ThemeToggle } from '@/src/components/theme-toggle'; // Import ThemeToggle

export function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { href: "#features", label: "Features" },
    { href: "#how-it-works", label: "How it Works" },
    { href: "#testimonials", label: "Testimonials" },
    { href: "#pricing", label: "Pricing" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        {/* Desktop Logo & Nav */}
        <div className="mr-4 hidden md:flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <Image src="/placeholder-logo.svg" alt="PixelChat Logo" width={32} height={32} />
            <span className="font-bold sm:inline-block">
              PixelChat
            </span>
          </Link>
          <nav className="flex items-center gap-6 text-sm">
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="transition-colors hover:text-foreground/80 text-foreground/60"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Mobile Nav Trigger & Logo */}
        <div className="flex items-center md:hidden flex-1">
           <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
             <SheetTrigger asChild>
               <Button variant="ghost" size="icon">
                 <HamburgerMenuIcon className="h-5 w-5" />
                 <span className="sr-only">Toggle Menu</span>
               </Button>
             </SheetTrigger>
             <SheetContent side="left">
               <nav className="grid gap-6 text-lg font-medium mt-6">
                 <Link href="/" className="flex items-center gap-2 text-lg font-semibold mb-4" onClick={() => setIsMobileMenuOpen(false)}>
                   <Image src="/placeholder-logo.svg" alt="PixelChat Logo" width={24} height={24} />
                   <span>PixelChat</span>
                 </Link>
                 {navItems.map((item) => (
                   <Link
                     key={item.label}
                     href={item.href}
                     className="hover:text-foreground text-muted-foreground"
                     onClick={() => setIsMobileMenuOpen(false)}
                   >
                     {item.label}
                   </Link>
                 ))}
                 <hr className="my-4"/>
                 <Button variant="ghost" asChild onClick={() => setIsMobileMenuOpen(false)}><Link href="#login">Log in</Link></Button>
                 <Button asChild onClick={() => setIsMobileMenuOpen(false)}><Link href="#start">Get Started</Link></Button>
               </nav>
             </SheetContent>
           </Sheet>
          {/* Mobile Centered Logo (Optional - if needed when menu is closed) */}
          <div className="flex justify-center flex-grow">
            <Link href="/" className="flex items-center space-x-2">
               <Image src="/placeholder-logo.svg" alt="PixelChat Logo" width={32} height={32} />
               <span className="font-bold">PixelChat</span>
            </Link>
          </div>
          {/* Spacer to push login/start buttons right */}
          <div className="w-10"></div> 
        </div>

        {/* Right Aligned Buttons (Desktop) */}
        <div className="hidden md:flex flex-1 items-center justify-end space-x-2">
          <Button variant="ghost">Log in</Button>
          <Button>Get Started</Button>
          <ThemeToggle /> {/* Add ThemeToggle here */}
        </div>
      </div>
    </header>
  );
} 