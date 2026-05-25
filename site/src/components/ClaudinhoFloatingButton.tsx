"use client"

import Image from "next/image"
import Link from "next/link"

/**
 * Botão flutuante do Claudinho da Brisa.
 * Por enquanto só visual — clique leva pra /claudinho que ainda não existe.
 * Será conectado ao chat real na Entrega 2.
 */
export function ClaudinhoFloatingButton() {
  return (
    <Link
      href="/claudinho"
      aria-label="Falar com o Claudinho da Brisa"
      className="fixed bottom-6 right-6 z-50 group flex items-center gap-3 bg-white border border-stone rounded-full pl-2 pr-5 py-2 shadow-sm hover:shadow-md hover:border-sand transition-all"
    >
      <span className="block w-10 h-10 rounded-full bg-[var(--color-bg-soft)] overflow-hidden flex items-center justify-center">
        <Image
          src="/claudinho/claudinho-avatar.png"
          alt=""
          width={40}
          height={40}
          className="object-cover"
        />
      </span>
      <span className="font-ui text-[10px] font-semibold uppercase tracking-[0.12em] text-coal/70 group-hover:text-green transition-colors hidden sm:block">
        Claudinho da Brisa
      </span>
    </Link>
  )
}
