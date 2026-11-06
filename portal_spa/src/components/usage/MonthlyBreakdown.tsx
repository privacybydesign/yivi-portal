import { Fragment, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  BILLED_FILTER,
  USAGE_ACTIONS,
  USAGE_OUTCOMES,
  credentialTypeTotals,
  currentPeriod,
  downloadMonthlyUsageCsv,
  fetchMonthlyUsage,
  gapDescription,
  gapPeriod,
  isBilledFilter,
  isFuturePeriod,
  periodLabel,
  requestorBreakdown,
  shiftPeriod,
  type MonthlyUsage,
  type UsageFilter,
  type UsagePeriod,
} from "@/actions/usage";
import { cn } from "@/lib/utils";

const formatCount = (n: number) => n.toLocaleString("en-US");

const LABELS: Record<string, string> = {
  disclosing: "Disclosure",
  signing: "Signature",
  issuing: "Issuance",
  done: "Done",
  cancelled: "Cancelled",
  failed: "Failed",
  timeout: "Timed out",
};

function ToggleGroup({
  label,
  options,
  selected,
  onChange,
}: {
  label: string;
  options: readonly string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm text-muted-foreground">{label}</span>
      <div role="group" aria-label={label} className="flex flex-wrap gap-1">
        {options.map((option) => {
          const pressed = selected.includes(option);
          return (
            <button
              key={option}
              type="button"
              aria-pressed={pressed}
              // At least one stays selected; an empty selection counts nothing.
              disabled={pressed && selected.length === 1}
              onClick={() =>
                onChange(
                  options.filter((o) =>
                    o === option ? !pressed : selected.includes(o),
                  ),
                )
              }
              className={cn(
                "cursor-pointer rounded-full border px-3 py-0.5 text-sm transition-colors disabled:cursor-not-allowed",
                pressed
                  ? "border-gray-900 bg-gray-900 text-white"
                  : "text-muted-foreground hover:bg-muted",
              )}
            >
              {LABELS[option] ?? option}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Completeness({ usage }: { usage: MonthlyUsage }) {
  const { complete, gaps } = usage.completeness;
  if (complete) {
    return (
      <p className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-900">
        Complete: your servers reported this whole period without gaps.
      </p>
    );
  }
  return (
    <div
      role="alert"
      className="space-y-2 rounded-lg border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-900"
    >
      <p className="font-medium">
        These numbers may be incomplete. The reports have{" "}
        {gaps.length === 1 ? "a gap" : `${gaps.length} gaps`}:
      </p>
      <ul className="list-disc space-y-1 pl-5">
        {gaps.map((gap) => (
          <li key={`${gap.kind}|${gap.server_instance}|${gap.from}`}>
            <span className="tabular-nums">{gapPeriod(gap)}</span>:{" "}
            {gapDescription(gap)}
          </li>
        ))}
      </ul>
      <p>
        For a period with a gap, invoicing relies on your own figures or an
        estimate.
      </p>
    </div>
  );
}

const resultKey = (slug: string, period: UsagePeriod, filter: UsageFilter) =>
  `${slug}|${period.year}-${period.month}|${filter.actions.join()}|${filter.outcomes.join()}`;

/**
 * One month's sessions and credentials per requestor and credential type, as
 * invoiced, with the gaps in the reports and a CSV export.
 */
export function MonthlyBreakdown({ slug }: { slug: string }) {
  const [period, setPeriod] = useState<UsagePeriod>(() =>
    currentPeriod("month"),
  );
  const [filter, setFilter] = useState<UsageFilter>(BILLED_FILTER);
  const [result, setResult] = useState<{
    key: string;
    usage: MonthlyUsage | null;
  } | null>(null);
  const [downloadError, setDownloadError] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const key = resultKey(slug, period, filter);
  useEffect(() => {
    let current = true;
    fetchMonthlyUsage(slug, period, filter)
      .then((usage) => current && setResult({ key, usage }))
      .catch(() => current && setResult({ key, usage: null }));
    return () => {
      current = false;
    };
  }, [slug, period, filter, key]);

  const shown = result?.key === key ? result : null;
  const usage = shown?.usage ?? null;
  const loadError = shown !== null && shown.usage === null;
  const next = shiftPeriod(period, 1);

  const download = async () => {
    setDownloading(true);
    setDownloadError(false);
    try {
      await downloadMonthlyUsageCsv(slug, period, filter);
    } catch {
      setDownloadError(true);
    } finally {
      setDownloading(false);
    }
  };

  const requestors = usage ? requestorBreakdown(usage) : [];
  const credentialTypes = usage ? credentialTypeTotals(usage) : [];
  const totalSessions = requestors.reduce((sum, r) => sum + r.sessions, 0);
  const totalCredentials = credentialTypes.reduce((sum, c) => sum + c.count, 0);

  return (
    <section className="space-y-4" aria-labelledby="breakdown-heading">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h3 id="breakdown-heading" className="text-base font-medium">
          Usage per credential type
        </h3>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            aria-label="Previous month, per credential type"
            onClick={() => setPeriod(shiftPeriod(period, -1))}
          >
            <ChevronLeft />
          </Button>
          <span
            className="min-w-32 text-center text-sm font-medium"
            aria-live="polite"
          >
            {periodLabel(period)}
          </span>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Next month, per credential type"
            disabled={isFuturePeriod(next)}
            onClick={() => setPeriod(next)}
          >
            <ChevronRight />
          </Button>
        </div>
      </div>

      <p className="text-sm text-muted-foreground">
        A session counts once under sessions, and once for every credential
        type it disclosed. By default this shows what is invoiced: completed
        disclosures and signatures.
      </p>

      <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
        <ToggleGroup
          label="Sessions"
          options={USAGE_ACTIONS}
          selected={filter.actions}
          onChange={(actions) => setFilter({ ...filter, actions })}
        />
        <ToggleGroup
          label="Outcome"
          options={USAGE_OUTCOMES}
          selected={filter.outcomes}
          onChange={(outcomes) => setFilter({ ...filter, outcomes })}
        />
        {!isBilledFilter(filter) && (
          <Button
            variant="link"
            size="sm"
            className="px-0"
            onClick={() => setFilter(BILLED_FILTER)}
          >
            Show what is invoiced
          </Button>
        )}
      </div>

      {loadError && (
        <p className="text-sm font-medium text-red-600">
          The usage per credential type could not be loaded. Please try again
          later.
        </p>
      )}

      {!usage && !loadError && (
        <div className="h-40 animate-pulse rounded-lg bg-muted" />
      )}

      {usage && (
        <>
          <Completeness usage={usage} />

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">Sessions</p>
              <p className="text-3xl font-semibold tabular-nums">
                {formatCount(totalSessions)}
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <p className="text-sm text-muted-foreground">Credentials</p>
              <p className="text-3xl font-semibold tabular-nums">
                {formatCount(totalCredentials)}
              </p>
            </div>
          </div>

          {requestors.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No sessions in {periodLabel(period)}.
            </p>
          ) : (
            <>
              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full text-sm">
                  <caption className="sr-only">
                    Credentials per credential type in {periodLabel(period)}
                  </caption>
                  <thead className="bg-muted/50 text-left">
                    <tr>
                      <th scope="col" className="px-3 py-2 font-medium">
                        Credential type
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-2 text-right font-medium"
                      >
                        Credentials
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {credentialTypes.map((c) => (
                      <tr key={c.credentialType} className="border-t">
                        <th
                          scope="row"
                          className="px-3 py-2 text-left font-mono font-normal break-all"
                        >
                          {c.credentialType}
                        </th>
                        <td className="px-3 py-2 text-right tabular-nums">
                          {formatCount(c.count)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full text-sm">
                  <caption className="sr-only">
                    Sessions and credentials per requestor in{" "}
                    {periodLabel(period)}
                  </caption>
                  <thead className="bg-muted/50 text-left">
                    <tr>
                      <th scope="col" className="px-3 py-2 font-medium">
                        Requestor and credential type
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-2 text-right font-medium"
                      >
                        Sessions
                      </th>
                      <th
                        scope="col"
                        className="px-3 py-2 text-right font-medium"
                      >
                        Credentials
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {requestors.map((r) => (
                      <Fragment key={r.requestor}>
                        <tr className="border-t bg-muted/20">
                          <th
                            scope="row"
                            className="px-3 py-2 text-left font-medium break-all"
                          >
                            {r.requestor || "(no requestor name)"}
                          </th>
                          <td className="px-3 py-2 text-right font-medium tabular-nums">
                            {formatCount(r.sessions)}
                          </td>
                          <td className="px-3 py-2" />
                        </tr>
                        {r.credentials.map((c) => (
                          <tr key={c.credentialType} className="border-t">
                            <th
                              scope="row"
                              className="py-1.5 pr-3 pl-8 text-left font-mono font-normal text-muted-foreground break-all"
                            >
                              {c.credentialType}
                            </th>
                            <td className="px-3 py-1.5" />
                            <td className="px-3 py-1.5 text-right tabular-nums">
                              {formatCount(c.count)}
                            </td>
                          </tr>
                        ))}
                      </Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          <div className="flex flex-wrap items-center gap-3">
            <Button variant="outline" onClick={download} disabled={downloading}>
              <Download />
              Download CSV
            </Button>
            {downloadError && (
              <p className="text-sm font-medium text-red-600">
                The CSV could not be downloaded. Please try again later.
              </p>
            )}
          </div>
        </>
      )}
    </section>
  );
}
