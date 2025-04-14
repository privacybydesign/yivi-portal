'use client';

import { fetchOrganization } from '@/src/actions/manage-organization';
import ManageOrganizationLayout from '@/src/components/layout/manage-organization';
import { Separator } from '@/src/components/ui/separator';
import { Organization } from '@/src/models/organization';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function RelyingParties() {
    const slug = useParams()?.organization;
    const [organization, setOrganization] = useState<Organization>();

    useEffect(() => {
        if (slug) {
            fetchOrganization(slug as string).then((response) => setOrganization(response?.data));
        }
    }, [slug]);

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-lg font-medium">Relying parties (TODO)</h2>
            </div>
            <Separator />
            <div>
                {organization?.name_en}
            </div>
        </div>
    );
}

RelyingParties.getLayout = ManageOrganizationLayout;