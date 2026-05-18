/* eslint-disable @typescript-eslint/no-explicit-any */
import { YiviCore } from "@privacybydesign/yivi-core";
import { YiviWeb } from "@privacybydesign/yivi-web";
import { YiviPopup } from "@privacybydesign/yivi-popup";
import { YiviClient } from "@privacybydesign/yivi-client";
import "@privacybydesign/yivi-css";

export interface YiviSession {
  start: (...input: unknown[]) => Promise<unknown>;
  abort: () => Promise<unknown>;
}

export function newWeb(options: any): YiviSession {
  const core = new YiviCore(options);
  core.use(YiviWeb);
  core.use(YiviClient);
  return {
    start: core.start.bind(core),
    abort: core.abort.bind(core),
  };
}

export function newPopup(options: any): YiviSession {
  const core = new YiviCore(options);
  core.use(YiviPopup);
  core.use(YiviClient);
  return {
    start: core.start.bind(core),
    abort: core.abort.bind(core),
  };
}
