import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useParams, Link } from "react-router-dom";
import { axiosInstance } from "@/services/axiosInstance";
import type { Organization } from "@/models/organization";
import type { RelyingParty } from "@/models/relying-party";

export default function OrganizationPage() {
  const params = useParams();
  const organizationSlug = params?.organization;

  const [organization, setOrganization] = useState<Organization | null>(null);
  const [rpDetails, setRpDetails] = useState<RelyingParty[]>([]);
  const [loadingRpDetails, setLoadingRpDetails] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState("overview");
  const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

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
        console.error("Error fetching organization:", error);
        setError(
          "Failed to load organization details. Please try again later."
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
        } catch (err) {
          console.warn(`Failed to fetch detail for RP ${rp.rp_slug}:`, err);
        }
      }

      setRpDetails(details);
    } catch (error) {
      console.error("Error fetching RP details:", error);
    } finally {
      setLoadingRpDetails(false);
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

    if (shouldFetchRpDetails) {
      fetchRelyingPartyDetails();
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

  if (error) {
    return <div className="p-4 bg-red-50 text-red-600 rounded-md">{error}</div>;
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
                to={`/trust-models/${encodeURIComponent(
                  organization.trust_model
                )}`}
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
            <Badge className="bg-blue-100 text-blue-800">Relying Party</Badge>
          )}
          {organization.is_verified && (
            <Badge className="bg-purple-100 text-purple-800">Verified</Badge>
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
                <span className="font-medium">ID:</span>
                <span className="col-span-2 font-mono text-sm">
                  {organization.id}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Slug:</span>
                <span className="col-span-2">{organization.slug}</span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Registration Number:</span>
                <span className="col-span-2">
                  {organization.registration_number}
                </span>
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
              <div className="grid grid-cols-3 gap-2">
                <span className="font-medium">Verified At:</span>
                <span className="col-span-2">
                  {formatDate(organization.verified_at)}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeSection === "ap-details" && organization.is_AP === true && (
        <Card>
          <CardHeader>
            <CardTitle>Attestation Provider Details</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-gray-600">
              This organization acts as an Attestation Provider in the
              {organization.trust_model} trust model.
            </p>
          </CardContent>
        </Card>
      )}

      {activeSection === "rp-details" && organization.is_RP === true && (
        <Card>
          <CardHeader>
            <CardTitle>Relying Party Details</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingRpDetails ? (
              <div className="py-8 text-center text-gray-500">
                Loading RP details...
              </div>
            ) : rpDetails.length > 0 ? (
              rpDetails.map((rp, index) => (
                <Card key={index} className="mb-6 border shadow-sm">
                  <CardHeader>
                    <CardTitle>
                      Relying Party: {rp.rp_slug}
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
                    <div className="pt-4 border-t">
                      <div className="flex flex-col gap-2 text-sm">
                        <div>
                          <span className="font-medium">Published At:</span>{" "}
                          {formatDate(rp.published_at)}
                        </div>
                      </div>
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
