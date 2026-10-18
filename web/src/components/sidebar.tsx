"use client";

import { useEffect, useRef, useState, useSyncExternalStore, type KeyboardEvent } from "react";
import { Icon, type IconName } from "./icon";

const items: { id: string; label: string; icon: IconName }[] = [
  { id: "genel-bakis", label: "Genel Bakış", icon: "overview" },
  { id: "erisim-denemeleri", label: "Erişim Denemeleri", icon: "records" },
  { id: "izinli-plakalar", label: "İzinli Plakalar", icon: "plates" },
  { id: "simulasyon", label: "Simülasyon", icon: "simulation" },
];

function subscribe(callback: () => void) {
  window.addEventListener("hashchange", callback);
  window.addEventListener("popstate", callback);
  return () => {
    window.removeEventListener("hashchange", callback);
    window.removeEventListener("popstate", callback);
  };
}
function getHash() { return window.location.hash; }
function getServerHash() { return ""; }

export function Sidebar() {
  const hash = useSyncExternalStore(subscribe, getHash, getServerHash);
  const active = items.find(({ id }) => `#${id}` === hash)?.id ?? "genel-bakis";
  const [open, setOpen] = useState(false);
  const [tooltipsDismissed, setTooltipsDismissed] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const destination = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!window.matchMedia) return;
    const desktop = window.matchMedia("(min-width: 768px)");
    const closeOnDesktop = () => { if (desktop.matches) dialog.current?.close(); };
    desktop.addEventListener("change", closeOnDesktop);
    return () => desktop.removeEventListener("change", closeOnDesktop);
  }, []);

  useEffect(() => {
    const dismissTooltips = (event: WindowEventMap["keydown"]) => {
      if (event.key === "Escape") setTooltipsDismissed(true);
    };
    window.addEventListener("keydown", dismissTooltips);
    return () => window.removeEventListener("keydown", dismissTooltips);
  }, []);

  function containFocus(event: KeyboardEvent<HTMLDialogElement>) {
    if (event.key !== "Tab") return;
    const controls = event.currentTarget.querySelectorAll<HTMLElement>("button, a[href]");
    const first = controls[0];
    const last = controls[controls.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  }

  function closeMenu() { dialog.current?.close(); }
  function restoreFocus() {
    setOpen(false);
    const desktopLink = window.matchMedia?.("(min-width: 768px)").matches
      ? document.querySelector<HTMLAnchorElement>(".sidebar-links [aria-current]")
      : null;
    (destination.current ?? desktopLink ?? trigger.current)?.focus();
    destination.current = null;
  }

  return <>
    <aside className="sidebar" aria-label="Kenar çubuğu">
      <a href="#genel-bakis" className="brand-mark" aria-label="Ana sayfa — Genel Bakış"><Icon name="plates" /></a>
      <nav aria-label="Ana gezinme" className="sidebar-links">
        {items.map((item) => <a key={item.id} href={`#${item.id}`} aria-current={active === item.id ? "location" : undefined} className="nav-link" aria-label={item.label} data-tooltip-dismissed={tooltipsDismissed || undefined} onMouseEnter={() => setTooltipsDismissed(false)} onFocus={() => setTooltipsDismissed(false)}>
          <Icon name={item.icon} /><span className="nav-tooltip">{item.label}</span>
        </a>)}
      </nav>
      <span className="sidebar-footnote" role="img" aria-label="Yalnızca simülasyon"><Icon name="shield" /></span>
    </aside>
    <button ref={trigger} type="button" className="mobile-menu-trigger icon-button" aria-label="Gezinme menüsünü aç" aria-expanded={open} aria-controls="mobile-navigation" aria-haspopup="dialog" onClick={() => { dialog.current?.showModal(); setOpen(true); }}><Icon name="menu" /></button>
    <dialog ref={dialog} id="mobile-navigation" className="mobile-navigation" aria-labelledby="navigation-title" onKeyDown={containFocus} onClose={restoreFocus} onCancel={() => setOpen(false)}>
      <div className="mobile-navigation-heading"><h2 id="navigation-title">Bölümler</h2><button type="button" className="icon-button" aria-label="Gezinme menüsünü kapat" onClick={closeMenu}><Icon name="close" /></button></div>
      <p className="text-secondary text-label">Akıllı Plaka Tanıma ve Bariyer Sistemi</p>
      <nav aria-label="Mobil gezinme" className="mobile-links">
        {items.map((item) => <a key={item.id} href={`#${item.id}`} className="mobile-nav-link" aria-current={active === item.id ? "location" : undefined} onClick={() => { destination.current = document.getElementById(item.id); closeMenu(); }}><Icon name={item.icon} /><span>{item.label}</span><Icon name="arrow" /></a>)}
      </nav>
      <p className="menu-disclaimer">Simülasyon · Fiziksel bariyer bağlı değil.</p>
    </dialog>
  </>;
}
