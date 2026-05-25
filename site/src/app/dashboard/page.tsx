import { Header } from "@/components/Header"
import { Footer } from "@/components/Footer"
import { EmConstrucao } from "@/components/EmConstrucao"
import { ClaudinhoFloatingButton } from "@/components/ClaudinhoFloatingButton"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Painel",
}

export default function DashboardPage() {
  return (
    <>
      <Header />
      <main>
        <EmConstrucao
          titulo="Painel"
          descricao="Status do projeto, marcos, infraestrutura e cronograma. Disponível para moradores e parceiros autenticados."
        />
      </main>
      <Footer />
      <ClaudinhoFloatingButton />
    </>
  )
}
