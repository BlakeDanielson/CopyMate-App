import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

// Update metadata to include music
export const metadata: Metadata = {
  title: "Blake Danielson | AI Product Developer & Music Producer",
  description:
    "Portfolio of Blake Danielson, an AI product developer and music producer building thoughtful AI for human experiences and creating original music compositions.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="dark bg-black">
      <head>
        <style>{`
          :root {
            color-scheme: dark;
          }
          body {
            background-color: black;
            color: white;
          }
          /* Fix for Next.js Image containers */
          [style*="position:relative"] > span > img[data-nimg="fill"],
          [style*="position: relative"] > span > img[data-nimg="fill"],
          span > img[data-nimg="fill"] {
            object-fit: cover !important;
          }
          /* Force position relative on all direct parent elements of fill images */
          span > img[data-nimg="fill"] {
            position: relative !important;
          }
        `}</style>
        <script dangerouslySetInnerHTML={{
          __html: `
            // Fix for image containers
            document.addEventListener('DOMContentLoaded', function() {
              // Force dark mode
              document.documentElement.classList.add('dark');
              document.documentElement.style.backgroundColor = 'black';
              document.body.style.backgroundColor = 'black';
              document.body.style.color = 'white';

              // Fix all img elements with data-nimg="fill"
              const fixImgContainers = () => {
                const imgElements = document.querySelectorAll('img[data-nimg="fill"]');
                imgElements.forEach(img => {
                  // Fix parent element
                  const parent = img.parentElement;
                  if (parent) {
                    parent.style.position = 'relative';
                    
                    // Also fix the parent of the parent (common Next.js structure)
                    const grandparent = parent.parentElement;
                    if (grandparent) {
                      grandparent.style.position = 'relative';
                    }
                  }
                });
              };
              
              // Run immediately and after small delay to catch any lazy-loaded images
              fixImgContainers();
              setTimeout(fixImgContainers, 500);
              setTimeout(fixImgContainers, 1500);
            });
          `
        }} />
      </head>
      <body className={`${inter.className} bg-black text-white`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false} forcedTheme="dark">
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
