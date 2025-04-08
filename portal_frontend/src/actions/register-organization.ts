"use server";

import { AxiosError } from "axios";
import { axiosInstance } from "../services/axiosInstance";
import { FieldErrors } from "react-hook-form";

export type RegistrationInputs = {
  name_en: string;
  name_nl: string;
  slug: string;
  registration_number: string;
  street: string;
  housenumber: string;
  postal_code: string;
  city: string;
  country: string;
  trade_names: string[];
  logo: File | undefined;
};

export type RegistrationFormState = {
  values: RegistrationInputs;
  errors: Partial<FieldErrors<RegistrationInputs>>;
  globalError?: string;
  success?: boolean;
  redirectTo?: string;
};

export const registerOrganization = async (
  formState: RegistrationFormState,
  formData: FormData
): Promise<RegistrationFormState> => {
  try {
    const response = await axiosInstance.post("/v1/organizations/", formData);
    const orgSlug = response.data?.slug;
    return {
      values: formState.values,
      errors: {},
      success: true,
      redirectTo: `/organizations/success?org=${orgSlug}`,
    };
  } catch (e: unknown) {
    console.log(e);
    if (e instanceof AxiosError && e.response?.status === 400) {
      const NewErrors: Partial<FieldErrors<RegistrationInputs>> = {};

      Object.entries(e.response.data).forEach(([key, value]) => {
        NewErrors[key as keyof RegistrationInputs] = {
          type: "server",
          message: String(value),
        };
      });
      return {
        values: formState.values,
        errors: NewErrors,
      };
    }
    return {
      values: formState.values,
      errors: {},
      globalError: "Something went wrong.",
    };
  }
};
