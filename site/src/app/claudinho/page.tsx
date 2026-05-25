import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { EmConstrucao } from "@/components/EmConstrucao"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Claudinho da Brisa",
}

export default function ClaudinhoPage() {
  return (
    <>
      <Header />
      <main>
        <EmConstrucao
          titulo="Claudinho da Brisa"
          descricao="Assistente contextualizado com toda a base de conhecimento e os documentos do projeto. Vai ser ativado na próxima entrega."
        />
      </main>
      <Footer />
    </>
  )
}
