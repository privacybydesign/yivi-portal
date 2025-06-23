import type { RelyingPartyFormData } from "@/components/forms/relying-party/validation-schema";
import type { RelyingParty } from "@/models/relying-party";

type RelyingPartyContextCommon = {
  defaultValues: RelyingPartyFormData;
  globalError?: string;
  isCreatingRP: boolean;
  onClose?: () => void;
  relyingParty?: RelyingParty;
};

type RelyingPartyEditContext = RelyingPartyContextCommon & {
  isEditMode: true;
  originalSlug: string;
  onSubmit: (data: Partial<RelyingPartyFormData>, originalSlug: string) => void;
};

type RelyingPartyCreateContext = RelyingPartyContextCommon & {
  isEditMode: false;
  originalSlug?: never;
  onSubmit: (data: RelyingPartyFormData) => void;
};

export type RelyingPartyContextValue =
  | RelyingPartyEditContext
  | RelyingPartyCreateContext;
