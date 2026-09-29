import { describe, expect, it } from "vitest";
import { bytes, count, dayTime, fullDate, midTrunc, plural, time } from "./format";

describe("format", () => {
  it("compte en français", () => {
    expect(count(184920).replace(/\s/gu, " ")).toBe("184 920");
  });

  it("accorde le nom au nombre", () => {
    expect(plural(0, "page")).toBe("0 page");
    expect(plural(1, "run")).toBe("1 run");
    expect(plural(4218, "page").replace(/\s/gu, " ")).toBe("4 218 pages");
  });

  it("passe au mégaoctet au-delà de 1 Mio", () => {
    expect(bytes(115_405)).toBe("113 KB");
    expect(bytes(4_089_446)).toBe("3.9 MB");
  });

  it("affiche l'heure locale d'un instant daté", () => {
    const iso = "2026-09-18T14:02:44Z";
    const local = new Date(iso);
    expect(time(iso)).toBe(local.toLocaleTimeString("fr-FR", { hour12: false }));
    expect(dayTime(iso)).toMatch(/^\d{2}\/\d{2} \d{2}:\d{2}$/u);
    expect(fullDate(iso)).toMatch(/^\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}$/u);
  });

  it("tronque au milieu", () => {
    expect(midTrunc("/abcdefghij", 7)).toBe("/ab…hij");
    expect(midTrunc("/court", 42)).toBe("/court");
  });
});
