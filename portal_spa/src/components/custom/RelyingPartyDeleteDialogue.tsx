import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

type RelyingPartyDeleteDialogueProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDelete: () => void;
  rpSlug: string;
  isDeleting: boolean;
};

export default function RelyingPartyDeleteDialogue({
  open,
  onOpenChange,
  onDelete,
  rpSlug,
  isDeleting,
}: RelyingPartyDeleteDialogueProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>Remove Relying Party</DialogTitle>
        <DialogDescription>
          Are you sure you want to remove the Relying Party "{rpSlug}"? This
          action cannot be undone.
        </DialogDescription>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={onDelete}
            disabled={isDeleting}
          >
            {isDeleting ? "Removing..." : "Remove"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function DeleteRelyingPartyButton({
  rpSlug,
  onOpenDialog,
}: {
  rpSlug: string;
  onOpenDialog: (rpSlug: string) => void;
}) {
  return (
    <Button
      variant="destructive"
      onClick={() => onOpenDialog(rpSlug)}
      className="px-1.5 text-sm"
    >
      Remove
    </Button>
  );
}
