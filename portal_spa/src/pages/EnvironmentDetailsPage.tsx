import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { axiosInstance } from "@/services/axiosInstance";
import { toast } from "sonner";
import type { YiviEnvironment } from "@/models/yivi-environment";
import { useParams } from "react-router-dom";
import { AxiosError } from "axios";

export default function EnvironmentDetailsPage() {
  const { environment: currentEnv } = useParams();
  const [yiviEnvironments, setYiviEnvironment] = useState<YiviEnvironment[]>(
    []
  );
  const [loading, setLoading] = useState(true);

  useEffect(
    () => window.scrollTo({ top: 0, behavior: "smooth" }),
    [currentEnv],
  );

  useEffect(() => {
    const fetchEnvironments = async () => {
      try {
        const response = await axiosInstance.get("/v1/yivi/environments/");
        setYiviEnvironment(response.data);
      } catch (error) {
        toast.error("Something went wrong", {
          description:
            error instanceof AxiosError
              ? error.message
              : "Please try again at a later time.",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchEnvironments();
  }, []);

  const selectedYiviEnvironment = currentEnv
    ? yiviEnvironments.filter((yiviEnv) => yiviEnv.environment === currentEnv)
    : [];

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-semibold">
        {currentEnv
          ? `${
              currentEnv.charAt(0).toUpperCase() + currentEnv.slice(1)
            } Environment`
          : "All Yivi Trust Model Environments"}
      </h1>

      {loading && (
        <p className="text-muted-foreground">Loading environments...</p>
      )}

      {!loading && selectedYiviEnvironment.length === 0 && (
        <p className="text-gray-500">No matching environments found.</p>
      )}

      {!loading &&
        selectedYiviEnvironment.map((yiviEnv) => (
          <Card key={yiviEnv.id}>
            <CardHeader>
              <CardTitle className="text-lg capitalize">
                Environment Details
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div>
                <span className="font-medium">ID:</span> {yiviEnv.scheme_id}
              </div>
              <div>
                <span className="font-medium">Name:</span> {yiviEnv.name_en}
              </div>
              <div>
                <span className="font-medium">Description:</span>{" "}
                {yiviEnv.description_en}
              </div>
              <div>
                <span className="font-medium">URL:</span>{" "}
                <a
                  href={`${yiviEnv.url}/description.xml`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {yiviEnv.url}
                </a>
              </div>
              <div>
                <span className="font-medium">Timestamp Server:</span>{" "}
                <a
                  href={yiviEnv.timestamp_server}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {yiviEnv.timestamp_server}
                </a>
              </div>
              <div>
                <span className="font-medium">Keyshare Server: </span>{" "}
                <a
                  href={yiviEnv.keyshare_server}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {yiviEnv.keyshare_server}
                </a>
              </div>
              <div>
                <span className="font-medium">Keyshare Website: </span>{" "}
                <a
                  href={yiviEnv.keyshare_website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {yiviEnv.keyshare_website}
                </a>
              </div>
              <div>
                <span className="font-medium">Keyshare Attribute: </span>{" "}
                {yiviEnv.keyshare_attribute}
              </div>
              <div>
                <span className="font-medium">Contact Website: </span>{" "}
                <a
                  href={yiviEnv.contact_website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {yiviEnv.contact_website}
                </a>
              </div>
            </CardContent>
          </Card>
        ))}
    </div>
  );
}
