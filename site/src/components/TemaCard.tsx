import Link from "next/link"
import { Tag } from "./Tag"
import type { Tema } from "@/lib/temas"

interface TemaCardProps {
  tema: Tema
}

export function TemaCard({ tema }: TemaCardProps) {
  const numFmt = String(tema.numero).padStart(2, "0")

  return (
    <Link
      href={`/conhecimento/${tema.slug}`}
      className="group block bg-white border border-stone rounded-md p-5 transition-all hover:border-sand hover:-translate-y-px"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="font-ui text-[10px] uppercase tracking-[0.15em] text-sand">
          Módulo {numFmt}
        </div>
        <Tag variant="green">
          {tema.meta.totalAulas} {tema.meta.totalAulas === 1 ? "aula" : "aulas"}
        </Tag>
      </div>
      <h3 className="font-serif text-lg leading-tight text-coal group-hover:text-green transition-colors">
        {tema.titulo}
      </h3>
      <p className="text-[13px] text-coal/55 leading-relaxed mt-3 line-clamp-3">
        {tema.visaoGeral.split("\n")[0]}
      </p>
    </Link>
  )
}
