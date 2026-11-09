import { AxiosError } from "axios";
import { axiosInstance } from "@/services/axiosInstance";

export interface UsageKey {
  id: string;
  label: string;
  thumbprint: string;
  created_at: string;
  deactivated_at: string | null;
  is_active: boolean;
}

export interface UsageSessionRow {
  day: string; // YYYY-MM-DD
  requestor: string;
  action: string;
  outcome: string;
  count: number;
}

export interface UsageGap {
  run_id: string;
  missing_count: number;
  final: boolean;
}

export interface UsageSummary {
  sessions: UsageSessionRow[];
  gaps: UsageGap[];
}

/** A calendar window: one month, or one year when `month` is absent. */
export interface UsagePeriod {
  kind: "month" | "year";
  year: number;
  month: number; // 1-12; ignored for a year
}

export interface UsageBucket {
  key: string;
  label: string; // axis label
  title: string; // full name, for the tooltip and the table
  count: number;
}

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const pad = (n: number) => String(n).padStart(2, "0");

const daysInMonth = (year: number, month: number) =>
  new Date(year, month, 0).getDate();

/** The period that holds `today`. Usage is counted per UTC day, so the period is taken in UTC. */
export const currentPeriod = (
  kind: UsagePeriod["kind"],
  today = new Date(),
): UsagePeriod => ({
  kind,
  year: today.getUTCFullYear(),
  month: today.getUTCMonth() + 1,
});

/** Moves a period one calendar month or year back (-1) or forward (+1). */
export const shiftPeriod = (period: UsagePeriod, step: number): UsagePeriod => {
  if (period.kind === "year") {
    return { ...period, year: period.year + step };
  }
  const index = period.year * 12 + (period.month - 1) + step;
  return { ...period, year: Math.floor(index / 12), month: (index % 12) + 1 };
};

export const isFuturePeriod = (period: UsagePeriod, today = new Date()) => {
  const now = currentPeriod(period.kind, today);
  if (period.kind === "year") return period.year > now.year;
  return period.year * 12 + period.month > now.year * 12 + now.month;
};

export const periodLabel = (period: UsagePeriod) =>
  period.kind === "year"
    ? String(period.year)
    : `${MONTHS[period.month - 1]} ${period.year}`;

/** The first and last day of the period, as the API's YYYY-MM-DD bounds. */
export const periodRange = (period: UsagePeriod) => {
  if (period.kind === "year") {
    return { from: `${period.year}-01-01`, to: `${period.year}-12-31` };
  }
  const last = daysInMonth(period.year, period.month);
  const prefix = `${period.year}-${pad(period.month)}`;
  return { from: `${prefix}-01`, to: `${prefix}-${pad(last)}` };
};

/** A verification is a disclosure session that completed. */
export const isSuccessfulVerification = (row: UsageSessionRow) =>
  row.action === "disclosing" && row.outcome === "done";

/**
 * Sums the successful verifications into one bucket per day of a month, or per
 * month of a year. Every day or month gets a bucket, so empty ones show as gaps
 * in the chart instead of disappearing.
 */
export const verificationBuckets = (
  rows: UsageSessionRow[],
  period: UsagePeriod,
): UsageBucket[] => {
  const buckets: UsageBucket[] =
    period.kind === "year"
      ? MONTHS.map((name, i) => ({
          key: `${period.year}-${pad(i + 1)}`,
          label: name.slice(0, 3),
          title: `${name} ${period.year}`,
          count: 0,
        }))
      : Array.from(
          { length: daysInMonth(period.year, period.month) },
          (_, i) => ({
            key: `${period.year}-${pad(period.month)}-${pad(i + 1)}`,
            label: String(i + 1),
            title: `${i + 1} ${MONTHS[period.month - 1]} ${period.year}`,
            count: 0,
          }),
        );
  const byKey = new Map(buckets.map((b) => [b.key, b]));
  for (const row of rows) {
    if (!isSuccessfulVerification(row)) continue;
    const key = period.kind === "year" ? row.day.slice(0, 7) : row.day;
    const bucket = byKey.get(key);
    if (bucket) bucket.count += row.count;
  }
  return buckets;
};

/** A round axis maximum with 4 even steps, e.g. 37 -> 40 (0, 10, 20, 30, 40). */
export const niceAxis = (max: number): number[] => {
  if (max <= 0) return [0, 1, 2, 3, 4];
  const rawStep = max / 4;
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const step =
    [1, 2, 2.5, 5, 10].map((m) => m * magnitude).find((s) => s >= rawStep) ??
    10 * magnitude;
  // Counts are whole numbers, so the axis steps are too (10 -> 0, 3, 6, 9, 12).
  const niceStep = Math.max(1, Math.ceil(step));
  return [0, 1, 2, 3, 4].map((i) => i * niceStep);
};

export const fetchUsageSummary = async (
  slug: string,
  period: UsagePeriod,
): Promise<UsageSummary> => {
  const response = await axiosInstance.get(`/v1/organizations/${slug}/usage/`, {
    params: periodRange(period),
  });
  return response.data;
};

export const fetchUsageKeys = async (slug: string): Promise<UsageKey[]> => {
  const response = await axiosInstance.get(
    `/v1/organizations/${slug}/usage-keys/`,
  );
  return response.data;
};

const apiError = (e: unknown, fallback: string) =>
  e instanceof AxiosError && typeof e.response?.data?.error === "string"
    ? e.response.data.error
    : fallback;

export const registerUsageKey = async (
  slug: string,
  publicKeyPem: string,
  label: string,
): Promise<{ key?: UsageKey; error?: string }> => {
  try {
    const response = await axiosInstance.post(
      `/v1/organizations/${slug}/usage-keys/`,
      { public_key_pem: publicKeyPem, label },
    );
    return { key: response.data };
  } catch (e) {
    // A 400 means the key did not parse; the API keeps its reason to itself.
    if (e instanceof AxiosError && e.response?.status === 400) {
      return {
        error:
          "That is not an EC P-256 public key. Paste the full output of `irma server usage-key`.",
      };
    }
    return { error: apiError(e, "The key could not be registered.") };
  }
};

export const deactivateUsageKey = async (
  slug: string,
  keyId: string,
): Promise<{ error?: string }> => {
  try {
    await axiosInstance.delete(
      `/v1/organizations/${slug}/usage-keys/${keyId}/`,
    );
    return {};
  } catch (e) {
    return { error: apiError(e, "The key could not be deactivated.") };
  }
};

// Monthly breakdown, for invoicing

export const USAGE_ACTIONS = ["disclosing", "signing", "issuing"] as const;
export const USAGE_OUTCOMES = ["done", "cancelled", "failed", "timeout"] as const;

/** What Trusted Verifiers are billed for: completed disclosures and signatures. */
export const BILLED_FILTER: UsageFilter = {
  actions: ["disclosing", "signing"],
  outcomes: ["done"],
};

export interface UsageFilter {
  actions: string[];
  outcomes: string[];
}

export interface MonthlySessionRow {
  requestor: string;
  action: string;
  outcome: string;
  count: number;
}

export interface MonthlyCredentialRow extends MonthlySessionRow {
  credential_type: string;
}

export type UsageGapKind =
  | "no_key"
  | "no_reports"
  | "missing_reports"
  | "interrupted"
  | "no_heartbeat";

export interface UsageMonthGap {
  kind: UsageGapKind;
  from: string;
  to: string;
  server_instance: string;
  missing_count?: number;
  irmago_version?: string;
}

export interface MonthlyUsage {
  month: string; // YYYY-MM
  actions: string[];
  outcomes: string[];
  sessions: MonthlySessionRow[];
  credentials: MonthlyCredentialRow[];
  completeness: {
    complete: boolean;
    reported_until: string | null;
    gaps: UsageMonthGap[];
  };
}

export interface CredentialTypeCount {
  credentialType: string;
  count: number;
}

export interface RequestorUsage {
  requestor: string;
  sessions: number;
  credentials: CredentialTypeCount[];
}

export const monthParam = (period: UsagePeriod) =>
  `${period.year}-${pad(period.month)}`;

export const isBilledFilter = (filter: UsageFilter) =>
  filter.actions.join() === BILLED_FILTER.actions.join() &&
  filter.outcomes.join() === BILLED_FILTER.outcomes.join();

const byCountThenName = (a: CredentialTypeCount, b: CredentialTypeCount) =>
  b.count - a.count || a.credentialType.localeCompare(b.credentialType);

const sumByCredentialType = (rows: MonthlyCredentialRow[]) => {
  const totals = new Map<string, number>();
  for (const row of rows) {
    totals.set(
      row.credential_type,
      (totals.get(row.credential_type) ?? 0) + row.count,
    );
  }
  return [...totals]
    .map(([credentialType, count]) => ({ credentialType, count }))
    .sort(byCountThenName);
};

/** Credentials per credential type over all requestors, most used first. */
export const credentialTypeTotals = (usage: MonthlyUsage) =>
  sumByCredentialType(usage.credentials);

/**
 * Sessions and credentials per requestor, most sessions first. Sessions come
 * from the session counts, never from the credentials: a session that
 * disclosed three credential types is one session.
 */
export const requestorBreakdown = (usage: MonthlyUsage): RequestorUsage[] => {
  const requestors = new Map<string, number>();
  for (const row of usage.sessions) {
    requestors.set(row.requestor, (requestors.get(row.requestor) ?? 0) + row.count);
  }
  for (const row of usage.credentials) {
    if (!requestors.has(row.requestor)) requestors.set(row.requestor, 0);
  }
  return [...requestors]
    .map(([requestor, sessions]) => ({
      requestor,
      sessions,
      credentials: sumByCredentialType(
        usage.credentials.filter((row) => row.requestor === requestor),
      ),
    }))
    .sort(
      (a, b) => b.sessions - a.sessions || a.requestor.localeCompare(b.requestor),
    );
};

const utcFormat = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "UTC",
});

export const gapPeriod = (gap: UsageMonthGap) =>
  `${utcFormat.format(new Date(gap.from))} – ${utcFormat.format(new Date(gap.to))} UTC`;

export const gapDescription = (gap: UsageMonthGap) => {
  const server = gap.server_instance || "A server";
  switch (gap.kind) {
    case "no_key":
      return "No usage key was active, so no server could report.";
    case "no_reports":
      return "No reports arrived from any of your servers.";
    case "missing_reports": {
      const n = gap.missing_count ?? 0;
      return `${server}: ${n} ${n === 1 ? "report" : "reports"} did not arrive.`;
    }
    case "interrupted":
      return `${server} stopped reporting without a final report; sessions after its last report are missing.`;
    case "no_heartbeat":
      return `${server} runs irmago ${gap.irmago_version || "of an older version"}, which sends no reports while it is quiet, so gaps cannot be detected. Upgrade the server to make this period verifiable.`;
  }
};

const monthlyParams = (period: UsagePeriod, filter: UsageFilter) => ({
  month: monthParam(period),
  action: filter.actions,
  outcome: filter.outcomes,
});

// Repeats array parameters (action=a&action=b), as Django's getlist expects.
const repeatParams = { indexes: null };

export const fetchMonthlyUsage = async (
  slug: string,
  period: UsagePeriod,
  filter: UsageFilter,
): Promise<MonthlyUsage> => {
  const response = await axiosInstance.get(
    `/v1/organizations/${slug}/usage/monthly/`,
    { params: monthlyParams(period, filter), paramsSerializer: repeatParams },
  );
  return response.data;
};

/** Downloads the month as CSV. The API needs the bearer token, so not a plain link. */
export const downloadMonthlyUsageCsv = async (
  slug: string,
  period: UsagePeriod,
  filter: UsageFilter,
): Promise<void> => {
  const response = await axiosInstance.get(
    `/v1/organizations/${slug}/usage/monthly/csv/`,
    {
      params: monthlyParams(period, filter),
      paramsSerializer: repeatParams,
      responseType: "blob",
    },
  );
  const url = URL.createObjectURL(response.data as Blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `yivi-usage-${slug}-${monthParam(period)}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};
