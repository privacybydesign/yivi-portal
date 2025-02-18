"use client";

import { useParams } from 'next/navigation';

export default function OrganizationPage() {
    const params = useParams();
    const organizationid = params.organizationid;

    return (
        <div className="container mx-auto px-4 py-10 text-left">
            <h1 className="text-3xl font-bold mb-4">{organizationid}</h1>
        </div>
    );
}