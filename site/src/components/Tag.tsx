import { cn } from "@/lib/cn"

interface TagProps {
  children: React.ReactNode
  variant?: "default" | "green"
  className?: string
}

const variants = {
  default: "bg-stone text-coal/70",
  green: "bg-green/10 text-green",
}

export function Tag({ children, variant = "default", className }: TagProps) {
  return (
    <span
      className={cn(
        "inline-block font-ui text-[9px] font-semibold uppercase tracking-[0.1em] px-2 py-0.5 rounded",
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  )
}
