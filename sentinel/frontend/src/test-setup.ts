if (typeof window !== "undefined") {
  window.scrollTo = () => {};
  // jsdom does no layout: no media query is evaluated.
  window.matchMedia ??= (media: string) =>
    ({
      media,
      matches: false,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList;

  // jsdom has <dialog> but not its modal behavior: only the open attribute exists.
  const dialog = window.HTMLDialogElement.prototype;
  dialog.showModal ??= function showModal(this: HTMLDialogElement) {
    this.open = true;
  };
  dialog.close ??= function close(this: HTMLDialogElement) {
    this.open = false;
    this.dispatchEvent(new Event("close"));
  };
}
