"use server";

import { AxiosError } from "axios";
import { axiosInstance } from "../services/axiosInstance";
import {
  RegistrationInputs,
  RegistrationFormState,
} from "../pages/organizations/register";
import { FieldErrors } from "react-hook-form";

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
