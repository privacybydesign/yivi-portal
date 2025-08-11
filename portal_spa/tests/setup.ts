import { expect, afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import * as matchers from "@testing-library/jest-dom/matchers";
import mock from "./mocks/api";

expect.extend(matchers);

afterEach(() => {
  cleanup();

  mock.resetHistory();
});
