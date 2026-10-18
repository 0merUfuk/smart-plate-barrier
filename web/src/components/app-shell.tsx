import type { ReactNode } from "react";
import { Sidebar } from "./sidebar";

export function AppShell({ children }: { children: ReactNode }) {
  return <div className="app-shell">
    <a href="#ana-icerik" className="skip-link">Ana içeriğe geç</a>
    <Sidebar />
    <div className="app-content">{children}</div>
  </div>;
}
