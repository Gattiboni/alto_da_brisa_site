import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { EmConstrucao } from "@/components/EmConstrucao"
import { ClaudinhoFloatingButton } from "@/components/ClaudinhoFloatingButton"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Galeria",
}

export default function GaleriaPage() {
  return (
    <>
      <Header />
      <main>
        <EmConstrucao
          titulo="Galeria"
          descricao="Fotos e vídeos do terreno, da natureza e da evolução do projeto. Em breve."
        />
      </main>
      <Footer />
      <ClaudinhoFloatingButton />
    </>
  )
}
