import { CopyButton } from "@/components/ui/copy-button";
import { cn } from "@/lib/utils";
import type { VariantProps } from "class-variance-authority";
import type { buttonVariants } from "./button";

export function CodeBlock({
  className,
  code,
  ...props
}: React.ComponentProps<"pre"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  } & { code: unknown }) {
  code = JSON.stringify(code, null, 2);

  return (
    <pre
      className={cn(
        "relative rounded-lg bg-muted p-4 group/code-block",
        className,
      )}
      {...props}
    >
      <code className="text-sm">{code as string}</code>
      <div className="absolute right-2 top-2 opacity-0 group-hover/code-block:opacity-100 transition-opacity">
        <CopyButton value={code as string} />
      </div>
    </pre>
  );
}
