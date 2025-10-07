import Link from "next/link"
import { Shield } from "lucide-react"

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 w-full pt-4">
      {/* This div is the centered, rounded, glass-effect pill */}
      <div
        className="
          mx-auto w-fit rounded-full border border-border/30 bg-background/80
          px-12 shadow-sm backdrop-blur-lg
          supports-[backdrop-filter]:bg-background/60
        "
      >
        <div className="flex h-14 items-center justify-between gap-6">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <Shield className="h-5 w-5" />
            <span className="font-sans">OS Forge</span>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link
              href="/"
              className="text-foreground/80 transition-colors hover:text-foreground"
            >
              Home
            </Link>
            <Link
              href="/dashboard"
              className="text-foreground/80 transition-colors hover:text-foreground"
            >
              Dashboard
            </Link>
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="text-foreground/80 transition-colors hover:text-foreground"
            >
              GitHub
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}