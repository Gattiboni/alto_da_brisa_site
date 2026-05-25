import Link from "next/link"
import { Container } from "./Container"

const NAV = [
  { href: "/conhecimento", label: "Conhecimento" },
  { href: "/galeria", label: "Galeria" },
  { href: "/dashboard", label: "Painel" },
]

export function Header() {
  return (
    <header className="border-b border-stone bg-white">
      <Container size="wide">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="group flex flex-col leading-none">
            <span className="font-ui text-[10px] font-medium uppercase tracking-[0.2em] text-sand">
              Sítio
            </span>
            <span className="font-serif text-lg tracking-wide text-green transition-colors group-hover:text-coal">
              Alto da Brisa
            </span>
          </Link>

          <nav className="flex items-center gap-1">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="font-ui text-[11px] font-medium uppercase tracking-[0.1em] text-coal/60 transition-colors hover:text-green px-3 py-2 rounded"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </Container>
    </header>
  )
}
