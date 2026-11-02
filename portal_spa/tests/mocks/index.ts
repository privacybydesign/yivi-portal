import { generateJwt } from "tests/utils";
import { vi } from "vitest";

vi.mock("@privacybydesign/yivi-frontend", () => ({
  newWeb: vi.fn(() => ({
    start: vi.fn(() =>
      Promise.resolve({
        access: generateJwt(),
      }),
    ),
    abort: vi.fn(),
  })),
}));
