import { AxiosError } from "axios";
import type { AxiosResponse } from "axios";
import { axiosInstance } from "../services/axiosInstance";
import type { FieldErrors } from "react-hook-form";
import useStore from "../store";

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
  logo: File | string | undefined;
  contact_number: string;
};

export type RegistrationFormState = {
  values: RegistrationInputs;
  errors: Partial<FieldErrors<RegistrationInputs>>;
  globalError?: string;
  success?: boolean;
  redirectTo?: string;
};

const updateClaims = async () => {
  const response = await axiosInstance.post("v1/refreshtoken", {
    update_claims: true,
  });

  axiosInstance.defaults.headers.common[
    "Authorization"
  ] = `Bearer ${response.data.access}`;

  const { setAccessToken } = useStore.getState();
  setAccessToken(response.data.access);

  return response.data.access;
};

export const fetchOrganization = async (
  organizationSlug: string
): Promise<AxiosResponse | undefined> => {
  try {
    return await axiosInstance.get(`/v1/organizations/${organizationSlug}/`);
  } catch (error) {
    console.error(error);
  }
};

export const updateOrganization = async (
  formState: RegistrationFormState,
  formData: FormData
): Promise<RegistrationFormState> => {
  if (
    !!formState.values["logo"] &&
    (formData.get("logo") as File)?.size === 0
  ) {
    formData.delete("logo");
  }

  try {
    await axiosInstance.patch(
      `/v1/organizations/${formState.values.slug}/update/`,
      formData
    );
    if (formData.get("slug") !== formState.values.slug) {
      await updateClaims();
      window.location.href = `/organizations/${formData.get("slug")}/manage`;
    }

    return {
      values: { ...formState.values },
      errors: {},
      success: true,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError && e.response?.status === 400) {
      const serverErrors: Partial<FieldErrors<RegistrationInputs>> = {};

      Object.entries(e.response.data).forEach(([key, value]) => {
        if (key !== "slug") {
          serverErrors[key as keyof Omit<RegistrationInputs, "slug">] = {
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

export const registerOrganization = async (
  formState: RegistrationFormState,
  formData: FormData
): Promise<RegistrationFormState> => {
  console.log(formState, formData);
  try {
    await axiosInstance.post("/v1/organizations/create/", formData);
    const slug = formData.get("slug") as string;

    await updateClaims();

    return {
      values: { ...formState.values },
      errors: {},
      success: true,
      redirectTo: `/organizations/${slug}/manage`,
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
