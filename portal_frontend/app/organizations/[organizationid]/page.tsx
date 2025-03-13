"use client";

import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from 'next/link';

// Define types
interface Organization {
  id: string;
  name_en: string;
  name_nl: string;
  slug: string;
  registration_number: string;
  address: string;
  is_verified: boolean;
  verified_at: string | null;
  trade_names: string[];
  logo: string;
  created_at: string;
  last_updated_at: string;
  is_RP: boolean;
  is_AP: boolean;
  trust_model: string;
}

interface Maintainer {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

// New RP Details type based on the API response
interface RPDetails {
  id: number;
  yivi_tme: string;
  organization: string;
  status: string | null;
  approved_rp_details: {
    id: string;
    logo: string;
    hostnames: string[];
    name: {
      en: string;
      nl: string;
    };
    scheme: string;
  };
  published_rp_details: {
    id: string;
    logo: string;
    hostnames: string[];
    name: {
      en: string;
      nl: string;
    };
    scheme: string;
  };
  created_at: string;
  last_updated_at: string;
}

export default function OrganizationPage() {
  const params = useParams();
  const organizationId = params.organizationid as string;
  
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [maintainers, setMaintainers] = useState<Maintainer[]>([]);
  const [rpDetails, setRpDetails] = useState<RPDetails | null>(null);
  const [loadingRpDetails, setLoadingRpDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState('overview');
  
  useEffect(() => {
    const fetchOrganizationData = async () => {
      try {
        // Fetch organization details
        const orgResponse = await axios.get(`http://0.0.0.0:8000/v1/organizations/${organizationId}/`);
        setOrganization(orgResponse.data);
        
        // Fetch maintainers
        try {
          const maintainersResponse = await axios.get(`http://0.0.0.0:8000/v1/organizations/${organizationId}/maintainers/`);
          setMaintainers(maintainersResponse.data);
        } catch (maintainersError) {
          console.error('Error fetching maintainers:', maintainersError);
          // Don't set error state, as this is not critical
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching organization:', error);
        setError('Failed to load organization details. Please try again later.');
        setLoading(false);
      }
    };
    
    if (organizationId) {
      fetchOrganizationData();
    }
  }, [organizationId]);
  
  // Handler for section changes with data fetching
  const handleSectionChange = (section: string) => {
    setActiveSection(section);
    
    // Fetch RP details when switching to RP details tab
    if (section === 'rp-details' && organization?.is_RP && !rpDetails && !loadingRpDetails) {
      setLoadingRpDetails(true);
      axios.get(`http://0.0.0.0:8000/v1/Yivi/production/relying-parties/`) // TODO : Fix Yivi having to be uppercase
        .then(response => {
          // Find the RP details for this organization
          const details = response.data.find(
            (rp: RPDetails) => rp.organization === organization.name_en
          );
          setRpDetails(details || null);
          setLoadingRpDetails(false);
        })
        .catch(error => {
          console.error('Error fetching RP details:', error);
          setLoadingRpDetails(false);
        });
    }
  };
  
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not available';
    return new Date(dateString).toLocaleString();
  };
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading organization details...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-600 rounded-md">
        {error}
      </div>
    );
  }
  
  if (!organization) {
    return (
      <div className="p-4 bg-yellow-50 text-yellow-600 rounded-md">
        Organization not found
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div className="flex items-center gap-4">
          {organization.logo && (
            <div className="relative h-16 w-16 rounded-full overflow-hidden border border-gray-200">
              <img 
                src={`http://0.0.0.0:8000${organization.logo}`} 
                alt={`${organization.name_en} logo`} 
                className="object-cover w-full h-full"
                onError={(e) => {
                  e.currentTarget.src = "/placeholder-logo.png"; 
                }}
              />
            </div>
          )}
          <div>
            <h1 className="text-3xl font-bold">{organization.name_en}</h1>
            <p className="text-gray-500">{organization.name_nl}</p>
            {organization.trust_model && (
              <Link 
                href={`/trust-models/${encodeURIComponent(organization.trust_model)}`}
                className="text-sm text-blue-600 hover:underline"
              >
                {organization.trust_model}
              </Link>
            )}
          </div>
        </div>
        
        <div className="flex gap-2">
          {organization.is_AP === true && (
            <Badge className="bg-green-100 text-green-800">
              Attestation Provider
            </Badge>
          )}
          {organization.is_RP === true && (
            <Badge className="bg-blue-100 text-blue-800">
              Relying Party
            </Badge>
          )}
          {organization.is_verified && (
            <Badge className="bg-purple-100 text-purple-800">
              Verified
            </Badge>
          )}
        </div>
      </div>
      
      <div className="flex mb-6 border-b">
        <button 
          className={`px-4 py-2 font-medium ${activeSection === 'overview' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
          onClick={() => handleSectionChange('overview')}
        >
          Overview
        </button>
        
        {organization.is_AP === true && (
          <button 
            className={`px-4 py-2 font-medium ${activeSection === 'ap-details' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
            onClick={() => handleSectionChange('ap-details')}
          >
            AP Details
          </button>
        )}
        
        {organization.is_RP === true && (
          <button 
            className={`px-4 py-2 font-medium ${activeSection === 'rp-details' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
            onClick={() => handleSectionChange('rp-details')}
          >
            RP Details
          </button>
        )}
        
        <button 
          className={`px-4 py-2 font-medium ${activeSection === 'maintainers' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
          onClick={() => handleSectionChange('maintainers')}
        >
          Maintainers
        </button>
      </div>
      
      {activeSection === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">ID:</span>
                <span className="col-span-2 font-mono text-sm">{organization.id}</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Slug:</span>
                <span className="col-span-2">{organization.slug}</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Registration Number:</span>
                <span className="col-span-2">{organization.registration_number}</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Address:</span>
                <span className="col-span-2">{organization.address}</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Status Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Created At:</span>
                <span className="col-span-2">{formatDate(organization.created_at)}</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Last Updated:</span>
                <span className="col-span-2">{formatDate(organization.last_updated_at)}</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Verified At:</span>
                <span className="col-span-2">{formatDate(organization.verified_at)}</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Trust Model:</span>
                <span className="col-span-2">{organization.trust_model || "Not specified"}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {activeSection === 'ap-details' && organization.is_AP === true && (
        <Card>
          <CardHeader>
            <CardTitle>Attestation Provider Details</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-gray-600">
              This organization acts as an Attestation Provider in the {organization.trust_model} trust model.
            </p>
            
            <div className="mt-4 p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium mb-2">Attestation Endpoints</h3>
              <div className="font-mono text-sm text-gray-700">
                <div className="mb-2">
                  <span className="text-blue-600">Issuance URL:</span> https://{organization.slug}.yivi.app/issue
                </div>
                <div>
                  <span className="text-blue-600">Verification URL:</span> https://{organization.slug}.yivi.app/verify
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {activeSection === 'rp-details' && organization.is_RP === true && (
        <Card>
          <CardHeader>
            <CardTitle>Relying Party Details</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingRpDetails ? (
              <div className="py-8 text-center text-gray-500">Loading RP details...</div>
            ) : rpDetails ? (
              <>
                <p className="mb-4 text-gray-600">
                  This organization acts as a Relying Party in the {rpDetails.yivi_tme} trust model.
                </p>
                
                <div className="mt-4 p-4 bg-gray-50 rounded-md">
                  <h3 className="font-medium mb-4">Integration Details</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium mb-2">Authorized Hostnames</h4>
                      <div className="bg-white p-3 rounded border">
                        {rpDetails.approved_rp_details.hostnames.length > 0 ? (
                          <ul className="list-disc list-inside space-y-1 font-mono text-sm">
                            {rpDetails.approved_rp_details.hostnames.map((hostname, index) => (
                              <li key={index}>{hostname}</li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-gray-500">No hostnames configured</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-sm font-medium mb-1">Scheme</h4>
                        <div className="font-mono text-sm bg-white p-2 rounded border">
                          {rpDetails.approved_rp_details.scheme}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium mb-1">RP Identifier</h4>
                        <div className="font-mono text-sm bg-white p-2 rounded border">
                          {rpDetails.approved_rp_details.id}
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-1">Status</h4>
                      <Badge className="bg-green-100 text-green-800">
                        {rpDetails.status || "Approved"}
                      </Badge>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 p-4 bg-gray-50 rounded-md">
                  <h3 className="font-medium mb-2">Publication Status</h3>
                  <div className="space-y-2">
                    <div>
                      <h4 className="text-sm font-medium">Last Published</h4>
                      <p className="text-gray-700">{formatDate(rpDetails.last_updated_at)}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium">Publication State</h4>
                      <Badge className="bg-blue-100 text-blue-800">
                        {JSON.stringify(rpDetails.approved_rp_details) === JSON.stringify(rpDetails.published_rp_details)
                          ? "Published"
                          : "Changes Pending"
                        }
                      </Badge>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-gray-600">
                <p>No detailed RP information found for this organization.</p>
                <p className="mt-2">This organization is registered as a Relying Party, but specific configuration details are not available.</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
      
      {activeSection === 'maintainers' && (
        <Card>
          <CardHeader>
            <CardTitle>Organization Maintainers</CardTitle>
          </CardHeader>
          <CardContent>
            {maintainers.length > 0 ? (
              <div className="space-y-4">
                {maintainers.map((maintainer) => (
                  <div key={maintainer.id} className="flex justify-between items-center p-3 border rounded-md">
                    <div>
                      <div className="font-medium">{maintainer.first_name} {maintainer.last_name}</div>
                      <div className="text-sm text-gray-500">{maintainer.email}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No maintainers found for this organization.</p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}