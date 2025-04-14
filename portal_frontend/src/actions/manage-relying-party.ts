"use server";

import { AxiosError } from "axios";
import { axiosInstance } from "../services/axiosInstance";
import { FieldErrors } from "react-hook-form";

export interface RelyingPartyInputs {
  rp_slug: string;
  hostnames: { hostname: string }[];
  trust_model_env: string;
  context_description_en: string;
  context_description_nl: string;
  attributes: {
    credential_attribute_tag: string;
    credential_attribute_name: string;
    reason_en: string;
    reason_nl: string;
  }[];
}

export type RelyingPartyFormState = {
  values: RelyingPartyInputs;
  errors: Partial<FieldErrors<RelyingPartyInputs>>;
  globalError?: string;
  success?: boolean;
  redirectTo?: string;
};

export async function fetchRelyingPartiesForOrganization(orgSlug: string) {
  return await fetch(`/api/organizations/${orgSlug}/relying-parties`).then(
    (res) => res.json()
  );
}

export async function fetchRelyingParty(slug: string) {
  return await fetch(`/api/relying-parties/${slug}`).then((res) => res.json());
}

export const updateRelyingParty = async (
  formState: RelyingPartyFormState,
  formData: FormData
): Promise<RelyingPartyFormState> => {
  try {
    await axiosInstance.patch(
      `/v1/organizations/[organization]/relying-party`,
      formData
    );

    return {
      values: { ...formState.values },
      errors: {},
      success: true,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError && e.response?.status === 400) {
      const serverErrors: Partial<FieldErrors<RelyingPartyInputs>> = {};

      Object.entries(e.response.data).forEach(([key, value]) => {
        if (key !== "slug") {
          serverErrors[key as keyof Omit<RelyingPartyInputs, "slug">] = {
            type: "server",
            message: String(value),
          };
        }
      });

      return {
        values: { ...formState.values },
        errors: serverErrors,
      };
    }

    return {
      values: { ...formState.values },
      errors: {},
      globalError: "Something went wrong.",
    };
  }
};

export const registerRelyingParty = async (
  formState: RelyingPartyFormState,
  formData: FormData
): Promise<RelyingPartyFormState> => {
  try {
    await axiosInstance.post(
      "/v1/organizations/[organization]/relying-party",
      formData
    );

    return {
      values: { ...formState.values },
      errors: {},
      success: true,
      redirectTo: `/organizations/success`,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError && e.response?.status === 400) {
      const serverErrors: Partial<FieldErrors<RelyingPartyInputs>> = {};

      Object.entries(e.response.data).forEach(([key, value]) => {
        serverErrors[key as keyof RelyingPartyInputs] = {
          type: "server",
          message: String(value),
        };
      });

      return {
        values: { ...formState.values },
        errors: serverErrors,
      };
    }

    return {
      values: { ...formState.values },
      errors: {},
      globalError: "Something went wrong.",
    };
  }
};
