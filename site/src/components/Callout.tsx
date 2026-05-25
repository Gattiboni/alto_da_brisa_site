import { cn } from "@/lib/cn"

interface CalloutProps {
  children: React.ReactNode
  title?: string
  className?: string
}

export function Callout({ children, title, className }: CalloutProps) {
  return (
    <aside
      className={cn(
        "border-l-2 border-green bg-green/5 px-5 py-4 my-6 rounded-r",
        className,
      )}
    >
      {title && (
        <div className="font-ui text-[10px] font-semibold uppercase tracking-[0.12em] text-green mb-2">
          {title}
        </div>
      )}
      <div className="text-coal/80 text-[14px] leading-relaxed">{children}</div>
    </aside>
  )
}
