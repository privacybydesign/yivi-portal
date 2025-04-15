"use server";

import { AxiosError, AxiosResponse } from "axios";
import { axiosInstance } from "../services/axiosInstance";
import { FieldErrors } from "react-hook-form";
import { RelyingParty } from "../models/relying-party";

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

export const fetchRelyingPartiesForOrganization = async (
  organizationSlug: string
): Promise<AxiosResponse | undefined> => {
  try {
    return await axiosInstance.get(
      `/v1/yivi/organizations/${organizationSlug}/relying-party`
    );
  } catch (error) {
    console.error(error);
  }
};

export const fetchDetailedRelyingPartiesForOrganization = async (
  organizationSlug: string
): Promise<RelyingParty[]> => {
  try {
    const listResponse = await fetchRelyingPartiesForOrganization(
      organizationSlug
    );
    const relyingPartyList = listResponse?.data?.relying_parties ?? [];

    const detailedParties = await Promise.all(
      relyingPartyList.map(
        async (rp: { rp_slug: string; environment: string }) => {
          try {
            const detailResponse = await axiosInstance.get(
              `/v1/yivi/organizations/${organizationSlug}/relying-party/${rp.environment}/${rp.rp_slug}`
            );

            return {
              ...detailResponse.data,
              environment: rp.environment,
            };
          } catch (err) {
            console.warn(`Failed to fetch detail for ${rp.rp_slug}`, err);
            return null;
          }
        }
      )
    );

    return detailedParties.filter(Boolean) as RelyingParty[];
  } catch (err) {
    console.error("Failed to fetch relying party list or details", err);
    return [];
  }
};

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
        if (key !== "relyingPartySlug") {
          serverErrors[
            key as keyof Omit<RelyingPartyInputs, "relyingPartySlug">
          ] = {
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
