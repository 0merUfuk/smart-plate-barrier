import { AppShell } from "../components/app-shell";
import { PageHeader } from "../components/page-header";
import { Icon } from "../components/icon";
import { Card } from "../components/ui/card";

export default function HomePage() {
  return <AppShell>
    <PageHeader />
    <main id="ana-icerik" tabIndex={-1} className="dashboard-grid">
      <Card id="genel-bakis" titleId="status-title" className="status-card">
        <div className="card-heading"><h2 id="status-title">Sanal bariyer</h2><span className="availability-label"><Icon name="link" />API bağlı değil</span></div>
        <div className="status-intro"><p className="status-value">Sanal durum bilinmiyor.</p><p className="text-secondary">API bağlantısı sonraki aşamada eklenecek.</p></div>
        <dl className="info-grid"><div><dt>Çalışma alanı</dt><dd>Sentetik demo</dd></div><div><dt>Veri kaynağı</dt><dd>Henüz bağlı değil</dd></div><div><dt>Fiziksel bağlantı</dt><dd>Donanım bağlı değil</dd></div></dl>
        <p className="safety-note"><Icon name="shield" />Sanal durum, fiziksel cihaz telemetrisi değildir.</p>
      </Card>

      <Card id="simulasyon" titleId="simulation-title" className="simulation-card">
        <span className="eyebrow">Deneme alanı</span><h2 id="simulation-title">Simülasyon</h2>
        <p className="text-secondary">Sentetik gözlem akışı burada yer alacak. Henüz işlem yapılamıyor.</p>
        <button className="primary-button" type="button" disabled aria-describedby="simulation-unavailable"><Icon name="simulation" /><span>Sentetik gözlem oluştur<span className="disabled-action-label">Önizleme · Kullanılamıyor</span></span></button>
        <p id="simulation-unavailable" className="text-caption text-secondary">API bağlantısı henüz yok. Bu aksiyon kullanılamıyor.</p>
      </Card>

      <Card titleId="attempts-summary" className="summary-card"><h2 id="attempts-summary">Yüklenen denemeler</h2><p className="unknown-value">Henüz sorgulanmadı</p><p className="text-secondary text-label">API bağlı değil; kayıt sayısı bilinmiyor.</p></Card>
      <Card titleId="allow-summary" className="summary-card"><h2 id="allow-summary">Bu kayıtlarda izin</h2><p className="unknown-value">Henüz sorgulanmadı</p><p className="text-secondary text-label">İzin kararı, fiziksel geçiş kanıtı değildir.</p></Card>
      <Card titleId="plates-summary" className="summary-card summary-wide"><h2 id="plates-summary">İzinli plakalar</h2><p className="unknown-value">Henüz sorgulanmadı</p><a href="#izinli-plakalar" className="text-link">İzinli plaka alanına git<Icon name="arrow" /></a></Card>

      <Card titleId="distribution-title" className="distribution-card">
        <div className="card-heading"><h2 id="distribution-title">Karar dağılımı</h2><span className="text-caption text-secondary">API bağlı değil</span></div>
        <div className="distribution-placeholder"><span className="placeholder-icon"><Icon name="distribution" /></span><p className="placeholder-title">Karar verileri henüz sorgulanmadı.</p><p className="text-secondary">Dağılım, yalnızca yüklenen erişim denemelerini gösterecek.</p></div>
        <p className="card-footer-note">Henüz veri bağlantısı yok; adet veya oran gösterilmiyor.</p>
      </Card>
      <Card titleId="recent-title" className="recent-card"><div className="card-heading"><h2 id="recent-title">Son gözlem</h2><Icon name="records" /></div><div className="recent-placeholder"><span className="eyebrow">Erişim kararı</span><p className="placeholder-title">Kayıt verileri henüz sorgulanmadı.</p><p className="text-secondary">API bağlantısı sonraki aşamada eklenecek. Bu alan gerçekleşmiş araç girişi veya çıkışı göstermez.</p></div></Card>

      <Card id="erisim-denemeleri" titleId="records-title" className="records-card"><div className="card-heading"><div><span className="eyebrow">Kayıtlar</span><h2 id="records-title">Erişim Denemeleri</h2></div><span className="section-symbol"><Icon name="records" /></span></div><div className="wide-placeholder"><p className="placeholder-title">Erişim denemeleri için ayrılan alan.</p><p className="text-secondary">Kayıt verileri henüz sorgulanmadı. API bağlantısı sonraki aşamada eklenecek; arama ve filtreleme henüz kullanılamıyor.</p></div></Card>

      <Card id="izinli-plakalar" titleId="plates-title" className="plates-card"><div className="card-heading"><div><span className="eyebrow">İzinli liste</span><h2 id="plates-title">İzinli Plakalar</h2></div><span className="section-symbol"><Icon name="plates" /></span></div><div className="wide-placeholder"><p className="placeholder-title">İzinli plaka verileri henüz sorgulanmadı.</p><p className="text-secondary">API bağlantısı ve liste yönetimi sonraki aşamalarda eklenecek.</p></div></Card>
    </main>
    <footer className="page-footer"><span>Geliştirme aşaması</span><span>Sentetik demo · Gerçek OCR veya fiziksel geçiş verisi yok.</span></footer>
  </AppShell>;
}
