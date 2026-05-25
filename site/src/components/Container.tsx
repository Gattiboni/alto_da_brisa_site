import { cn } from "@/lib/cn"

interface ContainerProps {
  children: React.ReactNode
  className?: string
  size?: "narrow" | "default" | "wide"
}

const sizes = {
  narrow: "max-w-2xl",
  default: "max-w-4xl",
  wide: "max-w-6xl",
}

export function Container({
  children,
  className,
  size = "default",
}: ContainerProps) {
  return (
    <div className={cn("mx-auto w-full px-6 md:px-8", sizes[size], className)}>
      {children}
    </div>
  )
}
