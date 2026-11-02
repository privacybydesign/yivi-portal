import { useState } from "react";
import { niceAxis, type UsageBucket } from "@/actions/usage";

const formatCount = (n: number) => n.toLocaleString("en-US");

/** Daily bars label every 5th day so a month's axis stays readable. */
const showLabel = (index: number, count: number) =>
  count <= 12 || index === 0 || (index + 1) % 5 === 0;

/**
 * Successful verifications as a single-series bar chart. Each bar is its own
 * hover and keyboard target; the same numbers are in a visually hidden table.
 */
export function VerificationsChart({
  buckets,
  caption,
}: {
  buckets: UsageBucket[];
  caption: string;
}) {
  const [active, setActive] = useState<number | null>(null);
  const ticks = niceAxis(Math.max(0, ...buckets.map((b) => b.count)));
  const axisMax = ticks[ticks.length - 1] ?? 1;
  const activeBucket = active === null ? null : buckets[active];

  return (
    <figure className="m-0">
      <div className="flex gap-2">
        {/* y-axis labels, aligned with the gridlines */}
        <div
          className="relative h-48 w-10 shrink-0 text-right text-xs text-muted-foreground"
          aria-hidden="true"
        >
          {ticks.map((tick) => (
            <span
              key={tick}
              className="absolute right-0 translate-y-1/2 tabular-nums leading-none"
              style={{ bottom: `${(tick / axisMax) * 100}%` }}
            >
              {formatCount(tick)}
            </span>
          ))}
        </div>

        <div className="relative min-w-0 flex-1">
          <div className="relative h-48">
            {ticks.map((tick) => (
              <div
                key={tick}
                aria-hidden="true"
                className={
                  tick === 0
                    ? "absolute inset-x-0 border-t border-gray-300"
                    : "absolute inset-x-0 border-t border-gray-100"
                }
                style={{ bottom: `${(tick / axisMax) * 100}%` }}
              />
            ))}

            <div
              role="group"
              aria-label={caption}
              className="absolute inset-0 flex items-end gap-[2px]"
              onPointerLeave={() => setActive(null)}
            >
              {buckets.map((bucket, i) => (
                <button
                  key={bucket.key}
                  type="button"
                  aria-label={`${bucket.title}: ${formatCount(bucket.count)} successful verifications`}
                  className="group flex h-full min-w-0 flex-1 cursor-default items-end rounded-sm outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
                  onPointerEnter={() => setActive(i)}
                  onFocus={() => setActive(i)}
                  onBlur={() => setActive(null)}
                >
                  <span
                    className="block w-full rounded-t-[4px] bg-[#2563eb] transition-colors group-hover:bg-[#3b82f6] group-focus-visible:bg-[#3b82f6]"
                    style={{ height: `${(bucket.count / axisMax) * 100}%` }}
                  />
                </button>
              ))}
            </div>

            {activeBucket && active !== null && (
              <div
                role="status"
                className="pointer-events-none absolute bottom-full z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md border bg-white px-2.5 py-1.5 text-sm shadow-md"
                style={{
                  left: `${((active + 0.5) / buckets.length) * 100}%`,
                }}
              >
                <div className="font-semibold tabular-nums text-foreground">
                  {formatCount(activeBucket.count)}
                </div>
                <div className="text-xs text-muted-foreground">
                  {activeBucket.title}
                </div>
              </div>
            )}
          </div>

          {/* x-axis labels */}
          <div
            className="mt-1 flex gap-[2px] text-xs text-muted-foreground"
            aria-hidden="true"
          >
            {buckets.map((bucket, i) => (
              <span key={bucket.key} className="min-w-0 flex-1 text-center">
                {showLabel(i, buckets.length) ? bucket.label : ""}
              </span>
            ))}
          </div>
        </div>
      </div>

      <figcaption className="sr-only">{caption}</figcaption>
      <table className="sr-only">
        <caption>{caption}</caption>
        <thead>
          <tr>
            <th scope="col">Period</th>
            <th scope="col">Successful verifications</th>
          </tr>
        </thead>
        <tbody>
          {buckets.map((bucket) => (
            <tr key={bucket.key}>
              <th scope="row">{bucket.title}</th>
              <td>{bucket.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
