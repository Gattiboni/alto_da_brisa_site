import { Container } from "./Container"

export function Footer() {
  return (
    <footer className="border-t border-stone bg-white mt-24">
      <Container size="wide">
        <div className="py-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="font-serif text-base text-green">Alto da Brisa</div>
            <div className="font-ui text-[10px] uppercase tracking-[0.15em] text-sand mt-1">
              Sapucaí-Mirim · Serra da Mantiqueira
            </div>
          </div>
          <div className="font-ui text-[10px] uppercase tracking-[0.12em] text-coal/40">
            Projeto pessoal · Em construção
          </div>
        </div>
      </Container>
    </footer>
  )
}
