import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import ManageOrganizationLayout from "@/components/layout/organization/manage-organization";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { UsageKeys } from "@/components/usage/UsageKeys";
import { VerificationsChart } from "@/components/usage/VerificationsChart";
import { fetchOrganization } from "@/actions/manage-organization";
import {
  currentPeriod,
  fetchUsageKeys,
  fetchUsageSummary,
  isFuturePeriod,
  periodLabel,
  shiftPeriod,
  verificationBuckets,
  type UsageKey,
  type UsagePeriod,
  type UsageSummary,
} from "@/actions/usage";
import { cn } from "@/lib/utils";

const KINDS: { kind: UsagePeriod["kind"]; label: string }[] = [
  { kind: "month", label: "Month" },
  { kind: "year", label: "Year" },
];

function PeriodControls({
  period,
  onChange,
}: {
  period: UsagePeriod;
  onChange: (period: UsagePeriod) => void;
}) {
  const next = shiftPeriod(period, 1);
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div
        role="group"
        aria-label="Time window"
        className="inline-flex rounded-md border p-0.5"
      >
        {KINDS.map(({ kind, label }) => (
          <button
            key={kind}
            type="button"
            aria-pressed={period.kind === kind}
            onClick={() => onChange(currentPeriod(kind))}
            className={cn(
              "cursor-pointer rounded px-3 py-1 text-sm font-medium transition-colors",
              period.kind === kind
                ? "bg-gray-900 text-white"
                : "text-muted-foreground hover:bg-muted",
            )}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Previous ${period.kind}`}
          onClick={() => onChange(shiftPeriod(period, -1))}
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
          aria-label={`Next ${period.kind}`}
          disabled={isFuturePeriod(next)}
          onClick={() => onChange(next)}
        >
          <ChevronRight />
        </Button>
      </div>
    </div>
  );
}

export default function UsageManagePage() {
  const { organization: slug } = useParams<{ organization: string }>();
  const [verified, setVerified] = useState<boolean | null>(null);
  const [keys, setKeys] = useState<UsageKey[]>([]);
  const [period, setPeriod] = useState<UsagePeriod>(() =>
    currentPeriod("month"),
  );
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  // Separate flags, so a period that loads clears only its own error.
  const [organizationError, setOrganizationError] = useState(false);
  const [keysError, setKeysError] = useState(false);
  const [usageError, setUsageError] = useState(false);

  useEffect(() => {
    if (!slug) return;
    // fetchOrganization answers undefined on any error; that says nothing
    // about verification, so only a real response sets `verified`.
    fetchOrganization(slug).then((response) => {
      if (response?.data) {
        setVerified(response.data.is_verified === true);
      } else {
        setOrganizationError(true);
      }
    });
  }, [slug]);

  const loadKeys = useCallback(() => {
    if (!slug) return;
    fetchUsageKeys(slug)
      .then((data) => {
        setKeys(data);
        setKeysError(false);
      })
      .catch(() => setKeysError(true));
  }, [slug]);

  useEffect(() => {
    if (verified) loadKeys();
  }, [verified, loadKeys]);

  useEffect(() => {
    if (!slug || !verified) return;
    let current = true;
    setSummary(null);
    setUsageError(false);
    fetchUsageSummary(slug, period)
      .then((data) => current && setSummary(data))
      .catch(() => current && setUsageError(true));
    return () => {
      current = false;
    };
  }, [slug, verified, period]);

  const buckets = summary ? verificationBuckets(summary.sessions, period) : [];
  const total = buckets.reduce((sum, b) => sum + b.count, 0);
  const incomplete = summary?.gaps.some((gap) => gap.missing_count > 0);

  return (
    <ManageOrganizationLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-medium">Usage</h2>
          <p className="text-sm text-muted-foreground">
            Verifications reported by your own Yivi servers.
          </p>
        </div>
        <Separator />

        {organizationError && (
          <p className="text-sm font-medium text-red-600">
            The organization could not be loaded. Please try again later.
          </p>
        )}

        {verified === null && !organizationError && <p>Loading...</p>}

        {verified === false && (
          <p className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-900">
            Usage reporting becomes available once your organization is
            verified. You can then register the keys of your Yivi servers here.
          </p>
        )}

        {verified && slug && (
          <>
            <section
              className="space-y-4"
              aria-labelledby="verifications-heading"
            >
              <div className="flex flex-wrap items-center justify-between gap-4">
                <h3
                  id="verifications-heading"
                  className="text-base font-medium"
                >
                  Successful verifications
                </h3>
                <PeriodControls period={period} onChange={setPeriod} />
              </div>

              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">
                  Total in {periodLabel(period)}
                </p>
                <p className="text-3xl font-semibold tabular-nums">
                  {summary ? total.toLocaleString("en-US") : "–"}
                </p>
              </div>

              {usageError && (
                <p className="text-sm font-medium text-red-600">
                  Usage could not be loaded. Please try again later.
                </p>
              )}

              {summary ? (
                <VerificationsChart
                  buckets={buckets}
                  caption={`Successful verifications per ${
                    period.kind === "month" ? "day" : "month"
                  } in ${periodLabel(period)}`}
                />
              ) : (
                !usageError && (
                  <div className="h-56 animate-pulse rounded-lg bg-muted" />
                )
              )}

              {incomplete && (
                <p className="text-sm text-muted-foreground">
                  Some reports from your servers have not arrived, so these
                  numbers may be incomplete.
                </p>
              )}
            </section>

            <Separator />

            {keysError && (
              <p className="text-sm font-medium text-red-600">
                The usage keys could not be loaded. Please try again later.
              </p>
            )}
            <UsageKeys slug={slug} keys={keys} onChange={loadKeys} />
          </>
        )}
      </div>
    </ManageOrganizationLayout>
  );
}
