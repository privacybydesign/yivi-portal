import { afterEach, beforeEach, expect, it } from "vitest";
import AxiosMockAdapter from "axios-mock-adapter";
import { generateJwt } from "tests/utils";
import { axiosInstance } from "@/services/axiosInstance";
import useStore from "@/store";

const mock = new AxiosMockAdapter(axiosInstance);

beforeEach(() => {
  mock.reset();
  useStore.getState().setAccessToken(null);
});

afterEach(() => {
  mock.reset();
});

it("does not attempt a refresh for anonymous visitors", async () => {
  mock.onPost("/v1/refreshtoken").reply(401, { detail: "Refresh token missing." });
  mock.onGet("/v1/yivi/all-credentials/").reply(200, []);

  await axiosInstance.get("/v1/yivi/all-credentials/");

  expect(mock.history.post).toHaveLength(0);
});

it("refreshes when the in-memory token has expired", async () => {
  useStore.getState().setAccessToken(generateJwt({ exp: 0 }));
  mock.onPost("/v1/refreshtoken").reply(200, { access: generateJwt() });
  mock.onGet("/v1/profile").reply(200, []);

  const response = await axiosInstance.get("/v1/profile");

  expect(mock.history.post).toHaveLength(1);
  expect(response.config.headers.Authorization).toMatch(/^Bearer /);
});

it("stops retrying once the session is gone", async () => {
  useStore.getState().setAccessToken(generateJwt({ exp: 0 }));
  mock.onPost("/v1/refreshtoken").reply(401, { detail: "Refresh token missing." });
  mock.onGet("/v1/profile").reply(200, []);

  await axiosInstance.get("/v1/profile");
  await axiosInstance.get("/v1/profile");

  // The dead session is cleared on the first failure, so the second request
  // goes out unauthenticated instead of firing another doomed refresh.
  expect(mock.history.post).toHaveLength(1);
  expect(useStore.getState().accessToken).toBeNull();
});
