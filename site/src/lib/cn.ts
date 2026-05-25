/**
 * Utilitário leve para concatenar classNames condicionais.
 * Sem dependência externa — clsx-like, suficiente para o projeto.
 */
type ClassValue = string | undefined | null | false | 0

export function cn(...inputs: ClassValue[]): string {
  return inputs.filter(Boolean).join(" ")
}
