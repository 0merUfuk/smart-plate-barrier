import type { ReactNode } from "react";

export function Card({ children, className = "", id, titleId }: { children: ReactNode; className?: string; id?: string; titleId: string }) {
  return <section id={id} aria-labelledby={titleId} tabIndex={id ? -1 : undefined} className={`card ${className}`}>{children}</section>;
}
