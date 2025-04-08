'use server';

import { AxiosError } from 'axios';
import { axiosInstance } from '../services/axiosInstance';
import { FieldErrors } from 'react-hook-form';

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

export const registerOrganization = async (state: { values: RegistrationInputs, errors: Partial<FieldErrors>; }, formData: FormData) => {
    try {
        await axiosInstance.post('/v1/organizations/', formData);

        // TODO: Redirect if it went well
    } catch (e) {
        if (e instanceof AxiosError && e.code === AxiosError.ERR_BAD_REQUEST) {
            for (const key in e.response?.data) {
                state.errors[key] = { message: e.response.data[key]?.join(' ') };
            }

            return state;
        }
    }

    return state;
};
