import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Lines a page up with the header's logo and account button at every width.
 *
 * The header lays out its contents as `container mx-auto px-4` across the
 * full viewport, while pages render inside <main>, which pads 16px. This steps
 * back out of that padding and repeats the header's own geometry, so the edges
 * match even just above a breakpoint, where <main>'s padding would otherwise
 * squeeze the container.
 */
export function PageContainer({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className="-mx-4">
      <div className={cn("container mx-auto px-4", className)}>{children}</div>
    </div>
  );
}
