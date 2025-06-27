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
  redirectTo?: string | undefined;
  cachedLogo?: File | null;
};

const updateClaims = async () => {
  const accessToken = await useStore.getState().refreshToken({
    update_claims: true,
  });

  axiosInstance.defaults.headers.common[
    "Authorization"
  ] = `Bearer ${accessToken}`;

  return accessToken;
};

const addCachedLogoToFormData = (
  formData: FormData,
  cachedLogo: File | undefined | null
): void => {
  const logo = formData.get("logo");
  if ((!logo || (logo instanceof File && logo.size === 0)) && cachedLogo) {
    formData.set("logo", cachedLogo);
    console.log("Adding cached logo to form data");
  }
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

  addCachedLogoToFormData(formData, formState.cachedLogo ?? undefined);

  try {
    await axiosInstance.patch(
      `/v1/organizations/${formState.values.slug}/update/`,
      formData
    );

    let redirectTo;
    if (formData.get("slug") !== formState.values.slug) {
      await updateClaims();
      // Can't use React router because middleware will be called before redirecting to the new page.
      window.location.href = `/organizations/${formData.get("slug")}/manage`;
    }

    return {
      values: { ...formState.values },
      errors: {},
      success: true,
      redirectTo,
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
  try {
    addCachedLogoToFormData(formData, formState.cachedLogo ?? undefined);

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
