'use client';

import { useToast } from '@/hooks/use-toast';
import { fetchMaintainersForOrganization, deleteMaintainerFromOrganization } from '@/src/actions/manage-maintainer';
import { fetchOrganization } from '@/src/actions/manage-organization';
import AddOrganizationMaintainerInformationForm from '@/src/components/forms/organization/maintainer';
import ManageOrganizationLayout from '@/src/components/layout/manage-organization';
import { Button } from '@/src/components/ui/button';
import { Separator } from '@/src/components/ui/separator';
import { Maintainer } from '@/src/models/maintainer';
import { Organization } from '@/src/models/organization';
import { X } from 'lucide-react';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ManageMaintainers() {
    const slug = useParams()?.organization;
    const [maintainers, setMaintainers] = useState<Maintainer[]>([]);
    const [organization, setOrganization] = useState<Organization>();
    const { toast } = useToast();

    const refreshMaintersForOrganization = (organisationSlug: string) => {
        fetchMaintainersForOrganization(organisationSlug).then((response) => setMaintainers(response?.data ?? []));
    };

    useEffect(() => {
        if (slug) {
            fetchOrganization(slug as string).then((response) => setOrganization(response?.data));
            refreshMaintersForOrganization(slug as string);
        }
    }, [slug]);

    const deleteMaintainer = async (maintainer: Maintainer) => {
        const { success, message } = await deleteMaintainerFromOrganization(maintainer, organization);
        refreshMaintersForOrganization(organization?.slug ?? '');

        toast({
            title: success ? 'Success' : 'Something went wrong',
            description: message
        });

    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-lg font-medium">Maintainers</h2>
                    <p className="text-sm text-muted-foreground">
                        Update your organization&apos;s maintainers.
                    </p>
                </div>
                {organization &&
                    <AddOrganizationMaintainerInformationForm organization={organization} onCreate={refreshMaintersForOrganization}></AddOrganizationMaintainerInformationForm>
                }
            </div>

            <Separator />

            <div className="space-y-4">
                {maintainers.map(maintainer => (
                    <div key={maintainer.id} className="space-y-2">
                        <div
                            className="flex justify-between items-center border p-3 rounded hover:bg-muted cursor-pointer"
                        >
                            <div>
                                <div className="font-medium">{maintainer.email}</div>
                                <div className="text-sm text-muted-foreground">
                                    {maintainer.role}
                                </div>
                            </div>
                            <Button variant="destructive" size="icon" onClick={() => deleteMaintainer(maintainer)}>
                                <X />
                                <span className="sr-only"></span>
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
        </div >
    );
}

ManageMaintainers.getLayout = ManageOrganizationLayout;