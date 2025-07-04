import type { StateStore } from "@/store";
import { generateJwt } from "tests/utils";
import { vi } from "vitest";
import { create, type StoreApi, type UseBoundStore } from "zustand";

vi.mock("@privacybydesign/yivi-frontend", async (importOriginal) => {
  return {
    ...(await importOriginal()),
    newWeb: vi.fn(() => ({
      start: vi.fn(() =>
        Promise.resolve({
          access: generateJwt(),
        }),
      ),
      abort: vi.fn(),
    })),
  };
});

vi.mock("@/store", async () => {
  // eslint-disable-next-line prefer-const
  let store: UseBoundStore<StoreApi<StateStore>>;

  const mockStore: StateStore = {
    accessToken: null,
    email: "",
    role: "maintainer",
    organizationSlugs: [],
    initialized: true,
    initializeAuth: () => new Promise(() => void 0),
    refreshToken: () => new Promise(() => ""),
    setAccessToken: vi.fn((accessToken) => {
      store.getState().accessToken = accessToken;
    }),
  };

  store = create(() => mockStore);

  return {
    __esModule: true,
    default: store,
    useIdleRefresh: vi.fn(),
  };
});
