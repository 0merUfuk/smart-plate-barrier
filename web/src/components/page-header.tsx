import { Icon } from "./icon";

export function PageHeader() {
  return <header className="page-header">
    <div className="page-identity"><p className="project-name">Akıllı Plaka Tanıma ve Bariyer Sistemi</p><h1>Genel Bakış</h1></div>
    <div className="header-context"><span className="mode-badge"><Icon name="simulation" />Simülasyon</span><p>Fiziksel bariyer bağlı değil.</p></div>
  </header>;
}
