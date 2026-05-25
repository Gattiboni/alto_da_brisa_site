"use client"

import { cn } from "@/lib/cn"

interface TocItem {
  id: string
  label: string
}

interface TocProps {
  items: TocItem[]
  activeId?: string
  className?: string
}

export function Toc({ items, activeId, className }: TocProps) {
  if (items.length === 0) return null

  return (
    <nav
      className={cn("sticky top-6 self-start", className)}
      aria-label="Navegação interna"
    >
      <div className="font-ui text-[10px] font-medium uppercase tracking-[0.15em] text-sand mb-3">
        Nesta página
      </div>
      <ul className="space-y-1 border-l border-stone/60">
        {items.map((item) => (
          <li key={item.id}>
            <a
              href={`#${item.id}`}
              className={cn(
                "block pl-4 py-1 -ml-px border-l text-[13px] transition-colors",
                activeId === item.id
                  ? "border-green text-green font-medium"
                  : "border-transparent text-coal/60 hover:text-coal hover:border-stone",
              )}
            >
              {item.label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}
