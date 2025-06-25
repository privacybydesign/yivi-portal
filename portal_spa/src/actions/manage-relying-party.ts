import { axiosInstance } from "@/services/axiosInstance";
import type { RelyingPartyFormData } from "@/components/forms/relying-party/validation-schema";
import type { FieldErrors } from "react-hook-form";
import { AxiosError } from "axios";
import type { RelyingParty } from "@/models/relying-party";
import type { Credential } from "@/models/credential";

export type RelyingPartyResponse<T = unknown> = {
  success: boolean;
  data?: T;
  fieldErrors?: Partial<FieldErrors<RelyingPartyFormData>>;
  globalError?: string;
};

export function parseDjangoErrorString(msg: string): string {
  if (msg.trim().startsWith("{") && msg.trim().endsWith("}")) {
    try {
      const jsonStr = msg.replace(/'/g, '"');
      const parsed = JSON.parse(jsonStr);
      return Object.values(parsed).flat().join(", ");
    } catch {
      return msg;
    }
  }
  return msg;
}

function transformAxiosError<T = unknown>(
  error: AxiosError
): RelyingPartyResponse<T> {
  if (error.response?.status === 400 && error.response.data) {
    return {
      success: false,
      fieldErrors: error.response.data,
    };
  }
  return {
    success: false,
    globalError: error.message,
  };
}

async function handleRequest<T>(
  fn: () => Promise<{ data: T }>
): Promise<RelyingPartyResponse<T>> {
  try {
    const response = await fn();
    return { success: true, data: response.data };
  } catch (error) {
    if (error instanceof AxiosError) {
      return transformAxiosError<T>(error);
    }
    return {
      success: false,
      globalError: "An unexpected error occurred.",
    };
  }
}

type FetchRelyingPartiesData = {
  relying_parties: RelyingParty[];
};

export async function fetchAllRelyingParties(
  organizationSlug: string
): Promise<RelyingPartyResponse<FetchRelyingPartiesData>> {
  try {
    const response = await axiosInstance.get(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/`
    );
    return { success: true, data: response.data };
  } catch (error) {
    if (error instanceof AxiosError) {
      return transformAxiosError<FetchRelyingPartiesData>(error);
    }
    return {
      success: false,
      globalError: "An unexpected error occurred.",
    };
  }
}

export async function fetchRelyingParty(
  organizationSlug: string,
  rpSlug: string,
  environment: string
): Promise<RelyingPartyResponse<RelyingParty>> {
  return handleRequest<RelyingParty>(() =>
    axiosInstance.get(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/${environment}/${rpSlug}/`
    )
  );
}

export async function updateRelyingParty(
  organizationSlug: string,
  data: Partial<RelyingPartyFormData>,
  originalSlug: string
): Promise<RelyingPartyResponse<RelyingParty>> {
  return handleRequest<RelyingParty>(() =>
    axiosInstance.patch(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/${originalSlug}/`,
      data
    )
  );
}

export async function registerRelyingParty(
  organizationSlug: string,
  data: RelyingPartyFormData
): Promise<RelyingPartyResponse<RelyingParty>> {
  return handleRequest<RelyingParty>(() =>
    axiosInstance.post(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/create/`,
      data
    )
  );
}

export async function deleteRelyingParty(
  organizationSlug: string,
  environment: string,
  rpSlug: string
): Promise<RelyingPartyResponse<null>> {
  return handleRequest<null>(() => {
    return axiosInstance.delete(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/${environment}/${rpSlug}/delete/`
    );
  });
}

export async function fetchCredentials(): Promise<
  RelyingPartyResponse<{ credentials: Credential[] }>
> {
  return handleRequest<{ credentials: Credential[] }>(() =>
    axiosInstance.get("/v1/yivi/credentials/")
  );
}
