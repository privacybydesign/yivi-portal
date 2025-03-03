"use client";

import { useParams } from 'next/navigation';
import { Organization, PaninatedResult} from "@/store";
import axiosInstance from '@/lib/axiosInstance';
import { useState, useEffect } from 'react';


export default function OrganizationPage() {
    const params = useParams();
    const organizationid = params.organizationid;

    const [organization, setOrganization] = useState<Organization>();

    useEffect(() => {
      axiosInstance.get<Organization>(`v1/organizations/${organizationid}`)
        .then(response => {
          setOrganization(response.data);
        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
    }, []);
  

    if (!organization) {
        return <div>Loading...</div>;
    }

    return (
        <div className="container mx-auto px-4 py-10 text-left">
            <h1 className="text-3xl font-bold mb-4">{organization.name_en}</h1>
            <p><strong>ID:</strong> {organization.id}</p>
            <p><strong>Name (EN):</strong> {organization.name_en}</p>
            <p><strong>Name (NL):</strong> {organization.name_nl}</p>
            <p><strong>Slug:</strong> {organization.slug}</p>
            <p><strong>Registration Number:</strong> {organization.registration_number}</p>
            <p><strong>Address:</strong> {organization.address}</p>
            <p><strong>Is Verified:</strong> {organization.is_verified ? 'Yes' : 'No'}</p>
            <p><strong>Verified At:</strong> {organization.verified_at}</p>
            <p><strong>Trade Names:</strong> {organization.trade_names.join(', ')}</p>
            <p><strong>Logo:</strong> <img src={organization.logo} alt={`${organization.name_en} logo`} /></p>
            <p><strong>Created At:</strong> {organization.created_at}</p>
            <p><strong>Last Updated At:</strong> {organization.last_updated_at}</p>
            <p><strong>Is RP:</strong> {organization.is_RP ? 'Yes' : 'No'}</p>
            <p><strong>Is AP:</strong> {organization.is_AP ? 'Yes' : 'No'}</p>
            <p><strong>Trust Model:</strong> {organization.trust_model}</p>
        </div>
    );
}