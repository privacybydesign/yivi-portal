import { AxiosError } from "axios";
import type { AxiosResponse } from "axios";
import { axiosInstance } from "@/services/axiosInstance";
import type { FieldErrors } from "react-hook-form";
import type { Maintainer } from "@/models/maintainer";
import type { Organization } from "@/models/organization";

export type MaintainerRegistrationInputs = {
  email: string;
  organizationSlug: string;
};

export type RegistrationFormState = {
  values: MaintainerRegistrationInputs;
  errors: Partial<FieldErrors<MaintainerRegistrationInputs>>;
  globalError?: string;
  success?: boolean;
  redirectTo?: string;
};

export const fetchMaintainersForOrganization = (
  organizationSlug: string
): Promise<AxiosResponse> => {
  return axiosInstance.get(
    `/v1/organizations/${organizationSlug}/maintainers/`
  );
};

export const addMaintainerForOrganization = async (
  formState: RegistrationFormState,
  formData: FormData
): Promise<RegistrationFormState> => {
  try {
    await axiosInstance.post(
      `/v1/organizations/${formState.values.organizationSlug}/maintainers/`,
      formData
    );

    return {
      values: formState.values,
      errors: {},
      success: true,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      if (e.response?.status === 400) {
        const serverErrors: Partial<FieldErrors<MaintainerRegistrationInputs>> =
          {};

        Object.entries(e.response.data).forEach(([key, value]) => {
          serverErrors[key as keyof MaintainerRegistrationInputs] = {
            type: "server",
            message: value as string,
          };
        });

        return {
          values: formState.values,
          errors: serverErrors,
        };
      }
      if (e.response?.status === 403) {
        return {
          values: formState.values,
          errors: {},
          globalError: Object.entries(e.response.data || {})
            .map(([, value]) => value as string)
            .join("; "),
        };
      }
    }
    return {
      values: formState.values,
      errors: {},
      globalError: "Something went wrong.",
    };
  }
};

export const deleteMaintainerFromOrganization = async (
  maintainer: Maintainer,
  organization?: Organization
): Promise<{ success: boolean; message: string }> => {
  if (!organization) {
    return { success: false, message: "No organization set" };
  }

  try {
    await axiosInstance.delete(
      `/v1/organizations/${organization.slug}/maintainers/${maintainer.id}/`
    );

    return {
      success: true,
      message: "User has been removed as maintainer from this organization",
    };
  } catch (e: unknown) {
    console.error(e);

    return { success: false, message: (e as AxiosError).toString() };
  }
};
