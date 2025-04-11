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
  house_number: string;
  postal_code: string;
  city: string;
  country: string;
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
    await axiosInstance.post("/v1/organizations/", formData);

    return {
      values: { ...formState.values, logo: formData.get('logo') as File },
      errors: {},
      success: true,
      redirectTo: `/organizations/success`,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError && e.response?.status === 400) {
      const serverErrors: Partial<FieldErrors<RegistrationInputs>> = {};

      Object.entries(e.response.data).forEach(([key, value]) => {
        serverErrors[key as keyof RegistrationInputs] = {
          type: "server",
          message: String(value),
        };
      });

      return {
        values: { ...formState.values, logo: formData.get('logo') as File },
        errors: serverErrors,
      };
    }

    return {
      values: { ...formState.values, logo: formData.get('logo') as File },
      errors: {},
      globalError: "Something went wrong.",
    };
  }
};
