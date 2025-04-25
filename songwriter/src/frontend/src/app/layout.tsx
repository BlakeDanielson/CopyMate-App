import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Songwriter Connect',
  description: 'A high-accuracy information portal focused on mainstream pop songwriters active from 2000 onwards.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="border-b">
          <div className="container mx-auto py-4 px-4 md:px-6 flex items-center justify-between">
            <Link href="/" className="text-xl font-semibold">
              Songwriter Connect
            </Link>
            <nav>
              <ul className="flex items-center gap-6">
                <li>
                  <Link 
                    href="/songwriters/1" 
                    className="text-sm font-medium hover:underline"
                  >
                    Max Martin
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/songwriters/2" 
                    className="text-sm font-medium hover:underline"
                  >
                    Finneas O'Connell
                  </Link>
                </li>
              </ul>
            </nav>
          </div>
        </header>
        <main>
          {children}
        </main>
        <footer className="border-t mt-12">
          <div className="container mx-auto py-6 px-4 md:px-6 text-center text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} Songwriter Connect (MVP v1.0)
          </div>
        </footer>
      </body>
    </html>
  )
} 