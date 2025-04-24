import { axiosInstance } from "../services/axiosInstance";
import { RelyingPartyFormData } from "../components/forms/relying-party/validation-schema";
import { FieldErrors } from "react-hook-form";
import { AxiosError } from "axios";
import { RelyingParty } from "../models/relying-party";

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
      hostnames: data.hostnames.map((h) => h.hostname),
    };
    const response = await axiosInstance.post(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/`,
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
