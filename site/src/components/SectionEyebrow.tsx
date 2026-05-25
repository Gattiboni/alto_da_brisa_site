import { cn } from "@/lib/cn"

interface SectionEyebrowProps {
  children: React.ReactNode
  className?: string
}

export function SectionEyebrow({ children, className }: SectionEyebrowProps) {
  return (
    <div
      className={cn(
        "font-ui text-[10px] font-medium uppercase tracking-[0.18em] text-sand mb-3",
        className,
      )}
    >
      {children}
    </div>
  )
}
