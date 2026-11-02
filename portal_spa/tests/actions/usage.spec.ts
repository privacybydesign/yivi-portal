import { describe, expect, it } from "vitest";
import {
  currentPeriod,
  isFuturePeriod,
  niceAxis,
  periodRange,
  shiftPeriod,
  verificationBuckets,
  type UsageSessionRow,
} from "@/actions/usage";

const row = (
  day: string,
  count: number,
  outcome = "done",
  action = "disclosing",
): UsageSessionRow => ({ day, count, outcome, action, requestor: "webshop" });

describe("calendar periods", () => {
  it("defaults to the current calendar month", () => {
    expect(currentPeriod("month", new Date(2026, 10, 2))).toEqual({
      kind: "month",
      year: 2026,
      month: 11,
    });
  });

  it("bounds a month by its first and last day, leap years included", () => {
    expect(periodRange({ kind: "month", year: 2028, month: 2 })).toEqual({
      from: "2028-02-01",
      to: "2028-02-29",
    });
    expect(periodRange({ kind: "year", year: 2026, month: 1 })).toEqual({
      from: "2026-01-01",
      to: "2026-12-31",
    });
  });

  it("steps over the turn of the year", () => {
    expect(shiftPeriod({ kind: "month", year: 2026, month: 1 }, -1)).toEqual({
      kind: "month",
      year: 2025,
      month: 12,
    });
    expect(shiftPeriod({ kind: "month", year: 2026, month: 12 }, 1)).toEqual({
      kind: "month",
      year: 2027,
      month: 1,
    });
  });

  it("knows which periods lie in the future", () => {
    const today = new Date(2026, 10, 2);
    expect(
      isFuturePeriod({ kind: "month", year: 2026, month: 11 }, today),
    ).toBe(false);
    expect(
      isFuturePeriod({ kind: "month", year: 2026, month: 12 }, today),
    ).toBe(true);
    expect(isFuturePeriod({ kind: "year", year: 2027, month: 1 }, today)).toBe(
      true,
    );
  });
});

describe("verificationBuckets", () => {
  const rows = [
    row("2026-11-02", 12),
    row("2026-11-02", 3), // another requestor on the same day
    row("2026-11-02", 5, "timeout"),
    row("2026-11-02", 7, "done", "issuing"),
    row("2026-11-30", 1),
  ];

  it("counts completed disclosure sessions per day of the month", () => {
    const buckets = verificationBuckets(rows, {
      kind: "month",
      year: 2026,
      month: 11,
    });
    expect(buckets).toHaveLength(30);
    expect(buckets[1]).toMatchObject({ label: "2", count: 15 });
    expect(buckets[29]?.count).toBe(1);
    expect(buckets.reduce((sum, b) => sum + b.count, 0)).toBe(16);
  });

  it("counts per month in a year", () => {
    const buckets = verificationBuckets([...rows, row("2026-01-15", 4)], {
      kind: "year",
      year: 2026,
      month: 1,
    });
    expect(buckets).toHaveLength(12);
    expect(buckets[0]).toMatchObject({ label: "Jan", count: 4 });
    expect(buckets[10]).toMatchObject({ label: "Nov", count: 16 });
  });
});

describe("niceAxis", () => {
  it("rounds the axis up to four even steps", () => {
    expect(niceAxis(37)).toEqual([0, 10, 20, 30, 40]);
    expect(niceAxis(1234)).toEqual([0, 500, 1000, 1500, 2000]);
    expect(niceAxis(3)).toEqual([0, 1, 2, 3, 4]);
    expect(niceAxis(0)).toEqual([0, 1, 2, 3, 4]);
  });

  it("keeps whole-number steps for whole-number counts", () => {
    expect(niceAxis(10)).toEqual([0, 3, 6, 9, 12]);
    expect(niceAxis(9)).toEqual([0, 3, 6, 9, 12]);
  });
});
