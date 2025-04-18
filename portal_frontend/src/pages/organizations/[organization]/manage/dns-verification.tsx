'use client';

import { fetchOrganization } from '@/src/actions/manage-organization';
import ManageOrganizationLayout from '@/src/components/layout/manage-organization';
import { Separator } from '@/src/components/ui/separator';
import { Organization } from '@/src/models/organization';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function DnsVerification() {
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
                <h2 className="text-lg font-medium">DNS verification (TODO)</h2>
                <p className="text-sm text-muted-foreground">
                    Verify your domains.
                </p>
            </div>
            <Separator />
            <div>
                {organization?.name_en}
            </div>
        </div>
    );
}

DnsVerification.getLayout = ManageOrganizationLayout;