import type { StateStore } from "@/store";
import { generateJwt } from "tests/utils";
import { vi } from "vitest";
import { create, type StoreApi, type UseBoundStore } from "zustand";

vi.mock("@privacybydesign/yivi-frontend", async (importOriginal) => ({
  ...(await importOriginal()),
  newWeb: vi.fn(() => ({
    start: vi.fn(() =>
      Promise.resolve({
        access: generateJwt(),
      }),
    ),
    abort: vi.fn(),
  })),
}));
