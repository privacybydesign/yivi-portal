import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useParams } from "react-router-dom";
import { axiosInstance, apiEndpoint } from "@/services/axiosInstance";
import type { Organization } from "@/models/organization";
import type { RelyingParty } from "@/models/relying-party";
import type { AttestationProvider } from "@/models/attestationprovider";
import { toast } from "sonner";

export default function OrganizationPage() {
  const params = useParams();
  const organizationSlug = params?.organization;

  const [organization, setOrganization] = useState<Organization | null>(null);
  const [rpDetails, setRpDetails] = useState<RelyingParty[]>([]);
  const [apDetails, setApDetails] = useState<AttestationProvider[]>([]);
  const [loadingApDetails, setLoadingApDetails] = useState(false);
  const [loadingRpDetails, setLoadingRpDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState("overview");

  useEffect(() => {
    const fetchOrganizationData = async () => {
      try {
        // Fetch organization details
        const orgResponse = await axiosInstance.get(
          `/v1/organizations/${organizationSlug}/`
        );
        setOrganization(orgResponse.data);

        setLoading(false);
      } catch (error) {
        toast.error(
          `Failed to load organization details: ${
            error instanceof Error ? error.message : String(error)
          }`
        );
        setLoading(false);
      }
    };

    if (organizationSlug) {
      fetchOrganizationData();
    }
  }, [organizationSlug]);

  const fetchRelyingPartyDetails = async () => {
    try {
      setLoadingRpDetails(true);

      const listResponse = await axiosInstance.get(
        `/v1/yivi/organizations/${organizationSlug}/relying-party/`
      );

      const rpList: RelyingParty[] = listResponse.data.relying_parties;

      const details: RelyingParty[] = [];

      for (const rp of rpList) {
        try {
          const detailResponse = await axiosInstance.get(
            `/v1/yivi/organizations/${organizationSlug}/relying-party/${rp.environment}/${rp.rp_slug}/`
          );
          const rpData = detailResponse.data;
          rpData.environment = rp.environment;

          details.push(detailResponse.data);
        } catch (error) {
          toast.error(
            `Failed to fetch details for ${rp.rp_slug} relying party: ${
              error instanceof Error ? error.message : String(error)
            }`
          );
        }
      }

      setRpDetails(details);
    } catch (error) {
      toast.error(
        `Failed to load relying parties for this organization: ${
          error instanceof Error ? error.message : String(error)
        }`
      );
    } finally {
      setLoadingRpDetails(false);
    }
  };

  const fetchAttestationProviderDetails = async () => {
    try {
      setLoadingApDetails(true);

      // Step 1: Get list of AP slugs and environments
      const listResponse = await axiosInstance.get(
        `/v1/yivi/organizations/${organizationSlug}/attestation-provider/`
      );

      const apList: Pick<AttestationProvider, "ap_slug" | "environment">[] =
        listResponse.data.attestation_providers;

      const details: AttestationProvider[] = [];

      // Step 2: For each, fetch full detail
      for (const ap of apList) {
        try {
          const detailResponse = await axiosInstance.get(
            `/v1/yivi/organizations/${organizationSlug}/attestation-provider/${ap.environment}/${ap.ap_slug}/`
          );
          const apData = detailResponse.data;
          apData.environment = ap.environment;
          details.push(apData);
        } catch (error) {
          toast.error(
            `Failed to fetch details for ${ap.ap_slug} attestation provider: ${
              error instanceof Error ? error.message : String(error)
            }`
          );
        }
      }

      setApDetails(details);
    } catch (error) {
      toast.error(
        `Failed to load attestation providers for this organization: ${
          error as string
        }`
      );
    } finally {
      setLoadingApDetails(false);
    }
  };

  // Handler for section changes with data fetching
  const handleSectionChange = (section: string) => {
    setActiveSection(section);

    const shouldFetchRpDetails =
      section === "rp-details" &&
      organization?.is_RP &&
      rpDetails.length === 0 &&
      !loadingRpDetails;

    const shouldFetchApDetails =
      section === "ap-details" &&
      organization?.is_AP &&
      apDetails.length === 0 &&
      !loadingApDetails;

    if (shouldFetchRpDetails) {
      fetchRelyingPartyDetails();
    }

    if (shouldFetchApDetails) {
      fetchAttestationProviderDetails();
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Not available";
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading organization details...</div>
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
                src={`${apiEndpoint}${organization.logo}`}
                width={50}
                height={50}
                alt={`${organization.name_en} logo`}
                className="object-cover w-full h-full"
                onError={(e) => {
                  e.currentTarget.src = "/logo-placeholder.svg";
                }}
              />
            </div>
          )}

          <div>
            <h1 className="text-3xl font-bold">{organization.name_en}</h1>
            <p className="text-gray-500">{organization.name_nl}</p>
            <div className="flex flex-wrap gap-1">
              {organization.trust_models?.map(
                (tm) =>
                  tm.name && (
                    <span
                      key={tm.name}
                      className="inline-block mt-2 px-2 py-1 text-sm font-medium text-gray-700 bg-gray-200 rounded-full"
                    >
                      {tm.name}
                    </span>
                  )
              )}
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          {organization.is_AP === true && (
            <Badge className="bg-purple-100 text-purple-800">
              Attestation Provider
            </Badge>
          )}
          {organization.is_RP === true && (
            <Badge className="bg-blue-100 text-blue-800">Relying Party</Badge>
          )}
          {organization.is_verified && (
            <Badge className="bg-green-100 text-green-800">Verified</Badge>
          )}
        </div>
      </div>

      <div className="flex mb-6 border-b">
        <button
          className={`px-4 py-2 font-medium ${
            activeSection === "overview"
              ? "border-b-2 border-blue-500 text-blue-600"
              : "text-gray-600"
          }`}
          onClick={() => handleSectionChange("overview")}
        >
          Overview
        </button>

        {organization.is_AP === true && (
          <button
            className={`px-4 py-2 font-medium ${
              activeSection === "ap-details"
                ? "border-b-2 border-blue-500 text-blue-600"
                : "text-gray-600"
            }`}
            onClick={() => handleSectionChange("ap-details")}
          >
            Attestation Provider
          </button>
        )}

        {organization.is_RP === true && (
          <button
            className={`px-4 py-2 font-medium ${
              activeSection === "rp-details"
                ? "border-b-2 border-blue-500 text-blue-600"
                : "text-gray-600"
            }`}
            onClick={() => handleSectionChange("rp-details")}
          >
            Relying Party
          </button>
        )}
      </div>

      {activeSection === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Slug:</span>
                <span className="col-span-2">{organization.slug}</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Country:</span>
                <span className="col-span-2">{organization.country}</span>
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
                <span className="col-span-2">
                  {formatDate(organization.created_at)}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Last Updated:</span>
                <span className="col-span-2">
                  {formatDate(organization.last_updated_at)}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeSection === "ap-details" && organization.is_AP === true && (
        <Card>
          <CardContent>
            <p className="mb-4 text-gray-600">
              The attestation providers listed below are configured for this
              organization. If the credential or attestation provider in certain
              environment has the deprecated flag, it means that it can no
              longer be used to issue the credentials.
            </p>
            {loadingApDetails ? (
              <div className="py-8 text-center text-gray-500">
                Loading AP details...
              </div>
            ) : (
              apDetails.map((ap, index) => (
                <div key={index}>
                  <Card key={index} className="mb-6 border shadow-sm">
                    <CardHeader>
                      <CardTitle>
                        {ap.ap_slug}{" "}
                        <span className="text-sm text-gray-500">
                          ({ap.environment})
                        </span>
                        {ap.deprecated_since && (
                          <Badge variant="destructive" className="ml-2">
                            Deprecated
                          </Badge>
                        )}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="text-sm text-gray-700">
                        <div>
                          <span className="font-medium "> Contact Email:</span>{" "}
                          {ap.contact_email}
                        </div>
                        <div className="mt-1">
                          <span className="font-medium">Contact Address:</span>{" "}
                          {ap.contact_address}
                        </div>

                        <div className="mt-1">
                          The following credentials can be issued by this
                          Attestation Provider.
                        </div>
                        <div className="text-sm text-gray-700 mt-2">
                          {ap.credentials.length === 0 ? (
                            <div className="text-gray-500">
                              No credentials available for this Attestation
                              Provider.
                            </div>
                          ) : (
                            <div className="grid grid-cols-1 gap-4">
                              {ap.credentials.map((cred, i) => (
                                <div
                                  key={i}
                                  className="p-6 border rounded-xl bg-gray-50 shadow-sm space-y-3"
                                >
                                  <div className="text-lg font-semibold text-gray-800 flex flex-wrap gap-2 items-center">
                                    {cred.name_en}

                                    <span className="text-sm text-gray-500 font-mono">
                                      ({cred.full_path})
                                    </span>
                                    {cred.deprecated_since && (
                                      <Badge
                                        variant="destructive"
                                        className="ml-2"
                                      >
                                        Deprecated
                                      </Badge>
                                    )}
                                  </div>

                                  <p className="text-sm text-gray-600">
                                    <span className="font-medium text-gray-700">
                                      Description:{" "}
                                    </span>
                                    {cred.description_en ||
                                      "No description available."}
                                  </p>

                                  <div>
                                    <p className="text-sm font-medium text-gray-700 mb-1">
                                      Attributes:
                                    </p>

                                    <ul className="list-disc list-inside text-gray-800 font-mono space-y-1">
                                      {cred.attributes.length > 0 ? (
                                        cred.attributes.map((attr) => (
                                          <li key={attr.id}>
                                            <span className="font-light">
                                              {attr.name_en}
                                            </span>{" "}
                                            <span className="text-gray-500">
                                              {attr.full_path}
                                            </span>
                                          </li>
                                        ))
                                      ) : (
                                        <li className="text-gray-400">
                                          No attributes defined
                                        </li>
                                      )}
                                    </ul>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      )}

      {activeSection === "rp-details" && organization.is_RP === true && (
        <Card>
          <CardContent>
            <p className="mb-4 text-gray-600">
              The relying parties listed below are configured for this
              organization.
            </p>
            {loadingRpDetails ? (
              <div className="py-8 text-center text-gray-500">
                Loading RP details...
              </div>
            ) : rpDetails.length > 0 ? (
              rpDetails.map((rp, index) => (
                <Card key={index} className="mb-6 border shadow-sm ">
                  <CardHeader>
                    <CardTitle>
                      {rp.rp_slug}{" "}
                      <span className="text-sm text-gray-500">
                        ({rp.environment})
                      </span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium">Authorized Hostnames</h4>
                      <ul className="list-disc list-inside text-sm font-mono">
                        {rp.hostnames.length > 0 ? (
                          rp.hostnames.map((h, i) => (
                            <li key={i}>{h.hostname}</li>
                          ))
                        ) : (
                          <li className="text-gray-500">
                            No hostnames registered
                          </li>
                        )}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="text-gray-600">
                No Relying Party configurations available for this organization.
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
