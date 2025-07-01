import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Link, useParams } from "react-router-dom";
import { axiosInstance, apiEndpoint } from "@/services/axiosInstance";
import type { Organization } from "@/models/organization";
import type { RelyingParty } from "@/models/relying-party";
import type { AttestationProvider } from "@/models/attestationprovider";
import { toast } from "sonner";
import { AlertTriangle } from "lucide-react";

export default function OrganizationPage() {
  const params = useParams();
  const organizationSlug = params?.organization;

  const [organization, setOrganization] = useState<Organization | null>(null);
  const [rpDetails, setRpDetails] = useState<RelyingParty[]>([]);
  const [apDetails, setApDetails] = useState<AttestationProvider[]>([]);
  const [loadingApDetails, setLoadingApDetails] = useState(false);
  const [loadingRpDetails, setLoadingRpDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState("");

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
  useEffect(() => {
    if (!organization) return;
    if (!activeSection) {
      if (organization.is_AP) {
        setActiveSection("ap-details");
      } else if (organization.is_RP) {
        setActiveSection("rp-details");
      }
    }

    // Fetch details based on the active section
    if (organization.is_RP && activeSection === "rp-details") {
      fetchRelyingPartyDetails();
    } else if (organization.is_AP && activeSection === "ap-details") {
      fetchAttestationProviderDetails();
    }
  }, [organization, activeSection]);

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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading organization details...</div>
      </div>
    );
  }

  if (!organization) {
    return (
      <div className="flex justify-center items-center min-h-[240px]">
        <Card className="max-w-lg w-full border-0 shadow-md bg-yellow-50">
          <CardContent className="flex items-center gap-4 py-8">
            <div className="flex-shrink-0">
              <AlertTriangle size={36} className="text-yellow-500" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-yellow-800 mb-1">
                Organization not found
              </h2>
              <p className="text-sm text-yellow-700">
                The organization you are looking for does not exist or is not
                available.
              </p>
            </div>
          </CardContent>
        </Card>
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
        {organization.is_AP === true && (
          <button
            className={`px-4 py-2 font-medium cursor-pointer ${
              activeSection === "ap-details"
                ? "border-b-2 border-blue-500 text-blue-600"
                : "text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-300"
            }`}
            onClick={() => handleSectionChange("ap-details")}
          >
            Attestation Provider
          </button>
        )}

        {organization.is_RP === true && (
          <button
            className={`px-4 py-2 font-medium cursor-pointer ${
              activeSection === "rp-details"
                ? "border-b-2 border-blue-500 text-blue-600"
                : "text-gray-600 hover:text-blue-600 hover:border-b-2 hover:border-blue-300"
            }`}
            onClick={() => handleSectionChange("rp-details")}
          >
            Relying Party
          </button>
        )}
      </div>

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
                <div className="text-lg font-semibold p-2" key={index}>
                  {ap.ap_slug}{" "}
                  <span className="text-sm text-gray-500">
                    ({ap.environment})
                  </span>
                  {ap.deprecated_since && (
                    <Badge variant="destructive" className="ml-2">
                      Deprecated
                    </Badge>
                  )}
                  <div className="text-sm text-gray-700 mx-2 mt-2">
                    <div className="mt-1">
                      <span className="font-medium "> Contact Email:</span>{" "}
                      <a
                        className="font-normal text-blue-600 hover:underline"
                        href={`mailto:${ap.contact_email}`}
                      >
                        {ap.contact_email}
                      </a>
                    </div>
                    <div className="mt-1">
                      <span className="font-medium">Contact Address:</span>{" "}
                      <a
                        className="font-normal text-blue-600 hover:underline"
                        href={`${ap.contact_address}`}
                      >
                        {ap.contact_address}
                      </a>
                    </div>
                    <div className="font-normal mt-1">
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
                        <div className="grid grid-cols-1 gap-3">
                          {ap.credentials.map((cred, i) => (
                            <div
                              key={i}
                              className="p-4 border rounded-lg bg-gray-50 shadow-sm hover:shadow-md transition-shadow"
                            >
                              <div className="flex flex-wrap gap-2 items-center justify-between">
                                <div className="flex flex-wrap gap-2 items-center">
                                  <h1 className="text-lg font-semibold text-gray-800">
                                    {cred.name_en}
                                  </h1>
                                  <span className="text-sm text-gray-500 font-mono">
                                    ({cred.full_path})
                                  </span>
                                </div>
                                <div className="flex gap-2">
                                  {cred.deprecated_since && (
                                    <Badge variant="destructive">
                                      Deprecated
                                    </Badge>
                                  )}
                                  <Link
                                    to={`/attribute-index/credentials/${ap.environment}/${ap.ap_slug}/${cred.credential_id}`}
                                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                                  >
                                    View Details →
                                  </Link>
                                </div>
                              </div>

                              {cred.description_en && (
                                <p className="text-sm text-gray-600 mt-2">
                                  {cred.description_en}
                                </p>
                              )}
                              <div className="mt-3"></div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
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
              rpDetails.map(
                (rp, index) =>
                  rp.status === "published" && (
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
                  )
              )
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
