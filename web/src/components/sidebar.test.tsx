import { afterEach, beforeAll, expect, test } from "vitest";
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import HomePage from "../app/page";

// JSDOM does not implement native modal lifecycle/focus containment.
// Only supply the missing dialog methods; native Escape and focus trapping
// are also verified in the real browser.
beforeAll(() => {
  if (!HTMLDialogElement.prototype.showModal) {
    HTMLDialogElement.prototype.showModal = function () { this.setAttribute("open", ""); };
  }
  if (!HTMLDialogElement.prototype.close) {
    HTMLDialogElement.prototype.close = function () {
      this.removeAttribute("open");
      this.dispatchEvent(new Event("close"));
    };
  }
});

afterEach(() => {
  cleanup();
  window.history.replaceState(null, "", "/");
});

test("every navigation and skip link has a unique, focusable real target", () => {
  const { container } = render(<HomePage />);
  for (const anchor of container.querySelectorAll<HTMLAnchorElement>('a[href^="#"]')) {
    const targets = container.querySelectorAll(anchor.hash);
    expect(targets.length).toBe(1);
    expect(targets[0].getAttribute("tabindex")).toBe("-1");
  }
});

test("deep links and history changes update the active section", () => {
  window.history.replaceState(null, "", "/#izinli-plakalar");
  render(<HomePage />);
  const navigation = within(screen.getByRole("navigation", { name: "Ana gezinme" }));
  expect(navigation.getByRole("link", { name: "İzinli Plakalar" }).getAttribute("aria-current")).toBe("location");
  act(() => {
    window.history.replaceState(null, "", "/#erisim-denemeleri");
    window.dispatchEvent(new PopStateEvent("popstate"));
  });
  expect(navigation.getByRole("link", { name: "Erişim Denemeleri" }).getAttribute("aria-current")).toBe("location");
  expect(navigation.getByRole("link", { name: "İzinli Plakalar" }).hasAttribute("aria-current")).toBe(false);
});

test("sidebar links use native hash navigation", async () => {
  const user = userEvent.setup();
  render(<HomePage />);
  const nav = within(screen.getByRole("navigation", { name: "Ana gezinme" }));
  await user.click(nav.getByRole("link", { name: "Erişim Denemeleri" }));
  await waitFor(() => expect(window.location.hash).toBe("#erisim-denemeleri"));
  await waitFor(() => expect(nav.getByRole("link", { name: "Erişim Denemeleri" }).getAttribute("aria-current")).toBe("location"));
});

test("mobile menu opens, closes, and returns focus to its trigger", async () => {
  const user = userEvent.setup();
  render(<HomePage />);
  const trigger = screen.getByRole("button", { name: "Gezinme menüsünü aç" });
  expect(trigger.getAttribute("aria-expanded")).toBe("false");
  await user.click(trigger);
  expect(screen.getByRole("dialog", { name: "Bölümler" }).hasAttribute("open")).toBe(true);
  expect(trigger.getAttribute("aria-expanded")).toBe("true");
  await user.click(screen.getByRole("button", { name: "Gezinme menüsünü kapat" }));
  expect(trigger.getAttribute("aria-expanded")).toBe("false");
  expect(document.activeElement).toBe(trigger);
});

test("native dialog cancellation restores closed state and trigger focus", async () => {
  const user = userEvent.setup();
  render(<HomePage />);
  const trigger = screen.getByRole("button", { name: "Gezinme menüsünü aç" });
  await user.click(trigger);
  const dialog = screen.getByRole("dialog", { name: "Bölümler" }) as HTMLDialogElement;
  // Browser Escape emits cancel, then closes the dialog. Reproduce that
  // lifecycle here; keyboard Escape itself is a separate browser check.
  fireEvent(dialog, new Event("cancel", { cancelable: true }));
  act(() => dialog.close());
  expect(trigger.getAttribute("aria-expanded")).toBe("false");
  expect(document.activeElement).toBe(trigger);
});

test("selecting a mobile destination closes the menu and focuses its section", async () => {
  const user = userEvent.setup();
  render(<HomePage />);
  await user.click(screen.getByRole("button", { name: "Gezinme menüsünü aç" }));
  const dialog = screen.getByRole("dialog", { name: "Bölümler" });
  await user.click(within(dialog).getByRole("link", { name: "İzinli Plakalar" }));
  expect(dialog.hasAttribute("open")).toBe(false);
  expect(document.activeElement?.id).toBe("izinli-plakalar");
  await waitFor(() => expect(window.location.hash).toBe("#izinli-plakalar"));
});

test("Tab and Shift+Tab stay within the open mobile menu", async () => {
  const user = userEvent.setup();
  render(<HomePage />);
  await user.click(screen.getByRole("button", { name: "Gezinme menüsünü aç" }));
  const dialog = screen.getByRole("dialog", { name: "Bölümler" });
  const close = within(dialog).getByRole("button", { name: "Gezinme menüsünü kapat" });
  const last = within(dialog).getByRole("link", { name: "Simülasyon" });
  close.focus();
  await user.tab({ shift: true });
  expect(document.activeElement).toBe(last);
  await user.tab();
  expect(document.activeElement).toBe(close);
});

test("simulation preview cannot be activated by pointer or keyboard and explains why", async () => {
  const user = userEvent.setup();
  const { container } = render(<HomePage />);
  const simulation = screen.getByRole("region", { name: "Simülasyon" });
  const button = within(simulation).getByRole("button", { name: /Sentetik gözlem oluştur/ }) as HTMLButtonElement;
  expect(button.disabled).toBe(true);
  expect(button.type).toBe("button");
  expect(button.textContent).toContain("Kullanılamıyor");
  const description = document.getElementById(button.getAttribute("aria-describedby") ?? "");
  expect(description?.textContent).toBe("API bağlantısı henüz yok. Bu aksiyon kullanılamıyor.");
  let activations = 0;
  button.addEventListener("click", () => { activations += 1; });
  const before = simulation.textContent;
  await user.click(button);
  await user.keyboard("{Enter} ");
  expect(activations).toBe(0);
  expect(simulation.textContent).toBe(before);
  container.querySelector<HTMLElement>("#ana-icerik")?.focus();
  await user.tab();
  expect(document.activeElement).toBe(screen.getByRole("link", { name: /İzinli plaka alanına git/ }));
});

test("unqueried data is distinct from empty results or an active request", () => {
  render(<HomePage />);
  const recent = within(screen.getByRole("region", { name: "Son gözlem" }));
  expect(recent.getByText("Kayıt verileri henüz sorgulanmadı.")).toBeTruthy();
  expect(recent.getByText(/API bağlantısı sonraki aşamada eklenecek/)).toBeTruthy();
  for (const title of ["Yüklenen denemeler", "Bu kayıtlarda izin", "İzinli plakalar"]) {
    expect(within(screen.getByRole("region", { name: title })).getByText("Henüz sorgulanmadı")).toBeTruthy();
  }
  expect(screen.getByText("Karar verileri henüz sorgulanmadı.")).toBeTruthy();
  expect(screen.getByText("İzinli plaka verileri henüz sorgulanmadı.")).toBeTruthy();
  expect(screen.getByText("Sanal durum bilinmiyor.")).toBeTruthy();
  expect(screen.queryByText(/Henüz bir kayıt alınmadı|Veri bekleniyor|Bağlantı bekleniyor/)).toBeNull();
  expect(document.querySelector('[aria-busy="true"]')).toBeNull();
});
