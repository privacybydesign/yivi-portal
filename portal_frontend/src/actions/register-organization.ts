'use server';

import { AxiosError } from 'axios';
import { axiosInstance } from '../services/axiosInstance';

export const registerOrganization = async (state: any, formData: FormData) => {
    console.log(state, formData);

    try {
        const response = await axiosInstance.post('/v1/organizations/', formData);

        console.debug('response from api', { response });
    } catch (e: any) {
        if (e.code === AxiosError.ERR_BAD_REQUEST) {
            for (const key in e.response.data) {
                state = {
                    ...state,
                    errors: {
                        ...state.errors,
                        [key]: { message: e.response.data[key].join(' ') }
                    }
                };
            }

            return state;
        }
    }

    // TODO: Redirect if it went well
};
