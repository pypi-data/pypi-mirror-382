"use client"

import { cn } from "@/lib/utils"
import { Card } from "@/components/ui/card"
import type { ReactNode } from "react"

type Props = {
  icon: ReactNode
  title: string
  description: string
  className?: string
}

export function FeatureCard({ icon, title, description, className }: Props) {
  return (
    <Card
      className={cn("px-4 py-3 rounded-xl shadow-sm border bg-background/70 backdrop-blur", className)}
      role="region"
      aria-label={title}
    >
      <div className="flex items-center gap-3">
        <div className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
          {icon}
        </div>
        <div>
          <div className="text-sm font-semibold text-foreground">{title}</div>
          <div className="text-xs text-muted-foreground">{description}</div>
        </div>
      </div>
    </Card>
  )
}
