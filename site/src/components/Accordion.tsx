"use client"

import { useState } from "react"
import { cn } from "@/lib/cn"

interface AccordionProps {
  title: string
  meta?: string
  children: React.ReactNode
  defaultOpen?: boolean
  className?: string
}

export function Accordion({
  title,
  meta,
  children,
  defaultOpen = false,
  className,
}: AccordionProps) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div
      className={cn(
        "border border-stone rounded-md overflow-hidden transition-colors",
        open && "border-sand",
        className,
      )}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-4 px-5 py-4 text-left bg-white hover:bg-[var(--color-bg-soft)] transition-colors"
        aria-expanded={open}
      >
        <div className="flex-1 min-w-0">
          <div className="font-serif text-base text-coal">{title}</div>
          {meta && (
            <div className="font-ui text-[10px] uppercase tracking-[0.1em] text-sand mt-1">
              {meta}
            </div>
          )}
        </div>
        <div
          className={cn(
            "flex-shrink-0 text-green text-sm transition-transform",
            open && "rotate-90",
          )}
          aria-hidden
        >
          ›
        </div>
      </button>
      {open && (
        <div className="px-5 py-5 bg-[var(--color-bg-soft)] border-t border-stone/60 text-[14px] leading-relaxed text-coal/85">
          {children}
        </div>
      )}
    </div>
  )
}
