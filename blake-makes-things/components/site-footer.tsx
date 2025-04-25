export function SiteFooter() {
  return (
    <footer className="border-t border-zinc-800 bg-black py-12">
      <div className="container px-4">
        <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-900/80 text-sm font-medium text-white">
              BD
            </span>
            <span className="text-sm font-medium text-white">Blake Danielson</span>
          </div>
          <div className="flex gap-6">
            <a
              href="https://www.linkedin.com/in/blakedan97/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-zinc-400 transition-colors hover:text-purple-400"
            >
              LinkedIn
            </a>
            <a
              href="https://github.com/BlakeDanielson"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-zinc-400 transition-colors hover:text-purple-400"
            >
              GitHub
            </a>
            <a
              href="https://soundcloud.com/blvkemusic"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-zinc-400 transition-colors hover:text-purple-400"
            >
              SoundCloud
            </a>
          </div>
          <div className="text-sm text-zinc-500">
            © {new Date().getFullYear()} Blake Danielson. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  )
}
