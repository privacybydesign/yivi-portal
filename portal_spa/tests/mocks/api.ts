import axios from "axios";
import AxiosMockAdapter from "axios-mock-adapter";
import { generateJwt, generateOrganization } from "tests/utils";

const mock = new AxiosMockAdapter(axios);

// The access token is kept in memory only; on load the SPA restores its
// session from the httpOnly refresh cookie by calling POST /v1/refreshtoken.
// Tests control this response to simulate an authenticated session (valid
// refresh cookie) or an unauthenticated one (missing/expired cookie).
let refreshResponse: [number] | [number, object] = [
  200,
  { access: generateJwt() },
];

export const setRefreshResponse = (status: number, claims?: object) => {
  refreshResponse =
    status === 200 ? [200, { access: generateJwt(claims) }] : [status];
};

export const resetRefreshResponse = () => {
  refreshResponse = [200, { access: generateJwt() }];
};

mock.onPost("/v1/refreshtoken").reply(() => refreshResponse);

mock
  .onGet(new RegExp(`/v1/organizations/*`))
  .reply(200, generateOrganization());

mock.onGet("/v1/profile").reply(200, [generateOrganization()]);

export default mock;
