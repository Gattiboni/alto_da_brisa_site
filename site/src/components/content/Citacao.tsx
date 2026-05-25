import { cn } from "@/lib/cn"

interface CitacaoProps {
  children: React.ReactNode
  atribuicao?: string
  className?: string
}

export function Citacao({ children, atribuicao, className }: CitacaoProps) {
  return (
    <figure
      className={cn(
        "my-8 md:my-10 text-center md:text-left",
        className,
      )}
    >
      <blockquote
        className={cn(
          "font-serif italic text-coal text-[22px] md:text-[26px]",
          "leading-[1.45]",
          "[&_p]:m-0 [&_p+p]:mt-3",
        )}
      >
        {children}
      </blockquote>
      {atribuicao && (
        <figcaption className="font-ui text-[11px] font-medium uppercase tracking-[0.1em] text-sand text-right mt-3">
          {atribuicao}
        </figcaption>
      )}
    </figure>
  )
}
