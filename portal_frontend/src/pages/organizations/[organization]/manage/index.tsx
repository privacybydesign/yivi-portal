'use client';

import { fetchOrganization } from '@/src/actions/manage-organization';
import ManageOrganizationInformationForm from '@/src/components/forms/organization/information';
import ManageOrganizationLayout from '@/src/components/layout/manage-organization';
import { Separator } from '@/src/components/ui/separator';
import { Organization } from '@/src/models/organization';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ManageLayout() {
    const slug = useParams()?.organization;
    const [organization, setOrganization] = useState<Organization>();

    useEffect(() => {
        if (slug) {
            fetchOrganization(slug as string)
                .then((response) => setOrganization(response?.data));
        }
    }, [slug]);

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-lg font-medium">Basic information</h2>
                <p className="text-sm text-muted-foreground">
                    Update your organization&apos;s basic information.
                </p>
            </div>
            <Separator />
            {organization && <ManageOrganizationInformationForm organization={organization}></ManageOrganizationInformationForm>}
        </div>
    );
}

ManageLayout.getLayout = ManageOrganizationLayout;