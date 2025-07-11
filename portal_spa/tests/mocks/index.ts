import { generateJwt } from "tests/utils";
import { vi } from "vitest";

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
