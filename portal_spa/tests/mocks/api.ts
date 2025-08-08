import axios from "axios";
import AxiosMockAdapter from "axios-mock-adapter";
import { generateJwt, generateOrganization } from "tests/utils";

const mock = new AxiosMockAdapter(axios);

mock.onPost("/v1/refreshtoken").reply(200, {
  access: generateJwt(),
});

mock
  .onGet(new RegExp(`/v1/organizations/*`))
  .reply(200, generateOrganization());

mock.onGet("/v1/profile").reply(200, [generateOrganization()]);

export default mock;
