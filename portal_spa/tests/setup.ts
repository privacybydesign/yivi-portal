import { expect, afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import * as matchers from "@testing-library/jest-dom/matchers";
import mock from "./mocks/api";

// Node exposes its own experimental `localStorage` global, which stays
// undefined without --localstorage-file and shadows the one jsdom would
// provide. Without a replacement every test touching auth state blows up on
// `localStorage.getItem`.
const createStorage = (): Storage => {
  let items = new Map<string, string>();

  return {
    get length() {
      return items.size;
    },
    clear: () => {
      items = new Map();
    },
    getItem: (key: string) => items.get(key) ?? null,
    key: (index: number) => [...items.keys()][index] ?? null,
    removeItem: (key: string) => {
      items.delete(key);
    },
    setItem: (key: string, value: string) => {
      items.set(key, String(value));
    },
  };
};

for (const name of ["localStorage", "sessionStorage"] as const) {
  if (!globalThis[name]) {
    Object.defineProperty(globalThis, name, {
      value: createStorage(),
      configurable: true,
      writable: true,
    });
  }
}

expect.extend(matchers);

afterEach(() => {
  cleanup();

  mock.resetHistory();
});
