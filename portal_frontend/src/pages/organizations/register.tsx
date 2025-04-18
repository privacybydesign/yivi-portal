"use client";

import ManageOrganizationInformationForm from '@/src/components/forms/organization/information';

export default function RegisterOrganization() {
    return (
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
            <div className="flex flex-col gap-6 mb-6">
                <h1 className="text-2xl font-bold mb-1">Register Organization</h1>
                <ManageOrganizationInformationForm></ManageOrganizationInformationForm>
            </div>
        </div>
    );
}
