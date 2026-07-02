import { expect, afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import * as matchers from "@testing-library/jest-dom/matchers";
import mock, { resetRefreshResponse } from "./mocks/api";

expect.extend(matchers);

afterEach(() => {
  cleanup();

  mock.resetHistory();
  resetRefreshResponse();
});
