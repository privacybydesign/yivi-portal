"use server";

import { AxiosError } from "axios";
import { axiosInstance } from "../services/axiosInstance";
import { FieldErrors } from "react-hook-form";
import { RelyingParty } from "../models/relying-party";

export interface RelyingPartyInputs {
  rp_slug: string;
  hostnames: { hostname: string }[];
  environment: string;
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
};

export const fetchRelyingPartiesForOrganization = async (
  organizationSlug: string
) => {
  try {
    const response = await axiosInstance.get(
      `/v1/yivi/organizations/${organizationSlug}/relying-party`
    );
    return response;
  } catch (error) {
    console.error("Error fetching relying parties:", error);
    return undefined;
  }
};

export const fetchDetailedRelyingParties = async (
  organizationSlug: string
): Promise<RelyingParty[]> => {
  try {
    const listResponse = await fetchRelyingPartiesForOrganization(
      organizationSlug
    );

    if (
      !listResponse ||
      !listResponse.data ||
      !listResponse.data.relying_parties
    ) {
      return [];
    }

    const relyingPartyList = listResponse.data.relying_parties;

    const detailedParties = await Promise.all(
      relyingPartyList.map(
        async (rp: { rp_slug: string; environment: string }) => {
          try {
            const detailResponse = await axiosInstance.get(
              `/v1/yivi/organizations/${organizationSlug}/relying-party/${rp.environment}/${rp.rp_slug}/`
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
  values: RelyingPartyInputs
): Promise<RelyingPartyFormState> => {
  try {
    // Extract hostname strings for the API - it expects a string array
    const hostnameStrings = values.hostnames
      .map((h) => h.hostname)
      .filter(Boolean);

    // Prepare the payload with flat hostnames array
    const payload = {
      ...values,
      hostnames: hostnameStrings,
    };

    const organizationSlug = "test-organization"; // TODO:

    await axiosInstance.patch(
      `/v1/yivi/organizations/${organizationSlug}/relying-party/${values.rp_slug}/`,
      payload
    );

    return {
      values,
      errors: {},
      success: true,
    };
  } catch (e) {
    if (e instanceof AxiosError && e.response?.status === 400) {
      const serverErrors: Partial<FieldErrors<RelyingPartyInputs>> = {};

      Object.entries(e.response.data).forEach(([key, value]) => {
        serverErrors[key as keyof RelyingPartyInputs] = {
          type: "server",
          message: String(value),
        };
      });

      return {
        values,
        errors: serverErrors,
      };
    }
    return {
      values,
      errors: {},
      globalError: "Something went wrong. Please try again.",
    };
  }
};

export const registerRelyingParty = async (
  values: RelyingPartyInputs
): Promise<RelyingPartyFormState> => {
  try {
    const hostnameStrings = values.hostnames
      .map((h) => h.hostname)
      .filter(Boolean);

    const payload = {
      ...values,
      hostnames: hostnameStrings,
    };

    const organizationSlug = "test-organization";

    await axiosInstance.post(
      `/v1/yivi/organizations/${organizationSlug}/relying-party`,
      payload
    );

    return {
      values,
      errors: {},
      success: true,
    };
  } catch (e) {
    if (e instanceof AxiosError && e.response?.status === 400) {
      const serverErrors: Partial<FieldErrors<RelyingPartyInputs>> = {};

      Object.entries(e.response.data).forEach(([key, value]) => {
        serverErrors[key as keyof RelyingPartyInputs] = {
          type: "server",
          message: String(value),
        };
      });

      return {
        values,
        errors: serverErrors,
      };
    }

    return {
      values,
      errors: {},
      globalError: "Something went wrong. Please try again.",
    };
  }
};
