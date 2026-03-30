import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Sítio Alto da Brisa',
  description: 'Em breve.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
