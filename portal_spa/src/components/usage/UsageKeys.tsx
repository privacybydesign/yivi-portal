import { useState } from "react";
import { toast } from "sonner";
import {
  deactivateUsageKey,
  registerUsageKey,
  type UsageKey,
} from "@/actions/usage";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

function RegisterKeyDialog({
  slug,
  onRegistered,
}: {
  slug: string;
  onRegistered: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [pem, setPem] = useState("");
  const [label, setLabel] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setPending(true);
    const result = await registerUsageKey(slug, pem, label);
    setPending(false);
    if (result.error) {
      setError(result.error);
      return;
    }
    toast.success("Key registered", {
      description: "This server can now send usage reports.",
    });
    setOpen(false);
    setPem("");
    setLabel("");
    setError(null);
    onRegistered();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Register key</Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={submit} className="space-y-4">
          <DialogHeader>
            <DialogTitle>Register a usage key</DialogTitle>
            <DialogDescription>
              Run <code>yivi irma server usage keygen</code> on your Yivi server and
              paste its full output.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="usage-key-pem">Public key</Label>
            <Textarea
              id="usage-key-pem"
              required
              rows={6}
              className="font-mono text-xs"
              placeholder={
                "-----BEGIN PUBLIC KEY-----\n…\n-----END PUBLIC KEY-----"
              }
              value={pem}
              onChange={(e) => setPem(e.target.value)}
              aria-invalid={error ? true : undefined}
              aria-describedby={error ? "usage-key-error" : undefined}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="usage-key-label">Label (optional)</Label>
            <Input
              id="usage-key-label"
              maxLength={255}
              placeholder="e.g. production server"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
            />
          </div>
          {error && (
            <p
              id="usage-key-error"
              className="text-sm font-medium text-red-600"
            >
              {error}
            </p>
          )}
          <DialogFooter>
            <Button type="submit" disabled={pending || !pem.trim()}>
              {pending ? "Registering..." : "Register"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function UsageKeys({
  slug,
  keys,
  onChange,
}: {
  slug: string;
  keys: UsageKey[];
  onChange: () => void;
}) {
  const deactivate = async (key: UsageKey) => {
    const name = key.label || key.thumbprint;
    if (
      !window.confirm(
        `Deactivate "${name}"? That server can no longer send reports. Reports it already sent are kept.`,
      )
    ) {
      return;
    }
    const result = await deactivateUsageKey(slug, key.id);
    if (result.error) {
      toast.error(result.error);
      return;
    }
    toast.success("Key deactivated");
    onChange();
  };

  return (
    <section className="space-y-4" aria-labelledby="usage-keys-heading">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 id="usage-keys-heading" className="text-base font-medium">
            Usage keys
          </h3>
          <p className="text-sm text-muted-foreground">
            Each Yivi server signs its usage reports with its own key.
          </p>
        </div>
        <RegisterKeyDialog slug={slug} onRegistered={onChange} />
      </div>

      {keys.length === 0 ? (
        <p className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
          No keys registered yet.
        </p>
      ) : (
        <ul className="divide-y rounded-lg border">
          {keys.map((key) => (
            <li
              key={key.id}
              className="flex items-center justify-between gap-4 p-4"
            >
              <div className="min-w-0 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="truncate font-medium">
                    {key.label || "Unlabelled key"}
                  </span>
                  {key.is_active ? (
                    <Badge
                      variant="secondary"
                      className="bg-green-100 text-green-800"
                    >
                      Active
                    </Badge>
                  ) : (
                    <Badge variant="secondary">Deactivated</Badge>
                  )}
                </div>
                <p
                  className="truncate font-mono text-xs text-muted-foreground"
                  title={key.thumbprint}
                >
                  {key.thumbprint}
                </p>
                <p className="text-xs text-muted-foreground">
                  Registered {formatDate(key.created_at)}
                  {key.deactivated_at &&
                    ` · deactivated ${formatDate(key.deactivated_at)}`}
                </p>
              </div>
              {key.is_active && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deactivate(key)}
                >
                  Deactivate
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
