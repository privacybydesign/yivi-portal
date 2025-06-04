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

// Fetch single RP
export async function fetchRelyingParty(
  organizationSlug: string,
  rpSlug: string,
  environment: string
): Promise<RelyingPartyResponse<RelyingParty>> {
  try {
    const response = await axiosInstance.get(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/${environment}/${rpSlug}/`
    );
    return { success: true, data: response.data };
  } catch (error) {
    if (error instanceof AxiosError) {
      return transformAxiosError<RelyingParty>(error);
    }
    return {
      success: false,
      globalError: "An unexpected error occurred.",
    };
  }
}

export async function updateRelyingParty(
  organizationSlug: string,
  data: Partial<RelyingPartyFormData>,
  originalSlug: string
): Promise<RelyingPartyResponse<RelyingParty>> {
  try {
    const payload: Partial<RelyingPartyFormData> = {
      ...data,
    };

    const response = await axiosInstance.patch(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/${originalSlug}/`,
      payload
    );
    return { success: true, data: response.data };
  } catch (error) {
    if (error instanceof AxiosError) {
      return transformAxiosError<RelyingParty>(error);
    }
    return {
      success: false,
      globalError: "An unexpected error occurred.",
    };
  }
}

// Register RP
export async function registerRelyingParty(
  organizationSlug: string,
  data: RelyingPartyFormData
): Promise<RelyingPartyResponse<RelyingParty>> {
  try {
    const payload = {
      ...data,
    };
    const response = await axiosInstance.post(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/create/`,
      payload
    );
    return { success: true, data: response.data };
  } catch (error) {
    if (error instanceof AxiosError) {
      return transformAxiosError<RelyingParty>(error);
    }
    return {
      success: false,
      globalError: "An unexpected error occurred.",
    };
  }
}
export async function deleteRelyingParty(
  organizationSlug: string,
  environment: string,
  rpSlug: string
): Promise<RelyingPartyResponse<null>> {
  try {
    await axiosInstance.delete(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/${environment}/${rpSlug}/delete/`
    );
    return { success: true };
  } catch (error) {
    if (error instanceof AxiosError) {
      return {
        success: false,
        globalError:
          error.response?.data?.detail || "Failed to delete the relying party.",
      };
    }
    return {
      success: false,
      globalError: "An unexpected error occurred.",
    };
  }
}

export async function fetchCredentials(): Promise<
  RelyingPartyResponse<{ credentials: Credential[] }>
> {
  try {
    const response = await axiosInstance.get("/v1/yivi/credentials/");
    return { success: true, data: response.data };
  } catch (error) {
    if (error instanceof AxiosError) {
      return transformAxiosError<{ credentials: Credential[] }>(error);
    }
    return {
      success: false,
      globalError: "An unexpected error occurred.",
    };
  }
}
