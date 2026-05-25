import { cn } from "@/lib/cn"

interface HighlightBoxProps {
  children: React.ReactNode
  className?: string
}

export function HighlightBox({ children, className }: HighlightBoxProps) {
  return (
    <div
      className={cn(
        "bg-[var(--color-bg-soft)] border border-stone/60 rounded-md px-6 py-5",
        className,
      )}
    >
      {children}
    </div>
  )
}
