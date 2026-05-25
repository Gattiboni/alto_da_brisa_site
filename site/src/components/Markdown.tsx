import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface MarkdownProps {
  children: string
}

/**
 * Renderiza markdown com estilo Alto da Brisa.
 * Tudo em prose-like custom, com tipografia serifada nos headings.
 */
export function Markdown({ children }: MarkdownProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="font-serif text-3xl text-coal mt-8 mb-4">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="font-serif text-2xl text-coal mt-8 mb-3">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="font-serif text-xl text-coal mt-6 mb-2">{children}</h3>
        ),
        h4: ({ children }) => (
          <h4 className="font-ui text-[11px] font-semibold uppercase tracking-[0.1em] text-coal/70 mt-5 mb-2">
            {children}
          </h4>
        ),
        p: ({ children }) => (
          <p className="text-coal/85 leading-relaxed mb-4">{children}</p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc pl-6 mb-4 space-y-1 text-coal/85 marker:text-sand">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal pl-6 mb-4 space-y-1 text-coal/85 marker:text-sand">
            {children}
          </ol>
        ),
        li: ({ children }) => <li className="leading-relaxed">{children}</li>,
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-green pl-4 my-4 italic text-coal/70">
            {children}
          </blockquote>
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            target={href?.startsWith("http") ? "_blank" : undefined}
            rel={href?.startsWith("http") ? "noopener noreferrer" : undefined}
            className="text-green hover:text-coal underline underline-offset-2 decoration-green/40 hover:decoration-coal/40 transition-colors"
          >
            {children}
          </a>
        ),
        strong: ({ children }) => (
          <strong className="text-coal font-semibold">{children}</strong>
        ),
        code: ({ children }) => (
          <code className="font-mono text-[13px] bg-stone/40 px-1.5 py-0.5 rounded">
            {children}
          </code>
        ),
        hr: () => <hr className="my-8 border-stone" />,
      }}
    >
      {children}
    </ReactMarkdown>
  )
}
