import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { axiosInstance } from "@/services/axiosInstance";
import { toast } from "sonner";
import type { Environment } from "@/models/environment";
import { useParams } from "react-router-dom";
import { AxiosError } from "axios";

export default function EnvironmentDetailsPage() {
  const { environment: currentEnv } = useParams();
  const [environments, setEnvironments] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEnvironments = async () => {
      try {
        const response = await axiosInstance.get("/v1/yivi/environments/");
        setEnvironments(response.data);
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

  const selectedEnvironment = currentEnv
    ? environments.filter((env) => env.environment === currentEnv)
    : environments;

  return (
    <div className="space-y-6 p-6">
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

      {!loading && selectedEnvironment.length === 0 && (
        <p className="text-gray-500">No matching environments found.</p>
      )}

      {!loading &&
        selectedEnvironment.map((env) => (
          <Card key={env.id}>
            <CardHeader>
              <CardTitle className="text-lg capitalize">
                Environment Details
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div>
                <span className="font-medium">ID:</span> {env.scheme_id}
              </div>
              <div>
                <span className="font-medium">Name:</span> {env.name_en}
              </div>
              <div>
                <span className="font-medium">Description:</span>{" "}
                {env.description_en}
              </div>
              <div>
                <span className="font-medium">URL:</span>{" "}
                <a
                  href={`${env.url}/description.xml`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {env.url}
                </a>
              </div>
              <div>
                <span className="font-medium">Timestamp Server:</span>{" "}
                <a
                  href={env.timestamp_server}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {env.timestamp_server}
                </a>
              </div>
              <div>
                <span className="font-medium">Keyshare Server: </span>{" "}
                <a
                  href={env.keyshare_server}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {env.keyshare_server}
                </a>
              </div>
              <div>
                <span className="font-medium">Keyshare Website: </span>{" "}
                <a
                  href={env.keyshare_website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {env.keyshare_website}
                </a>
              </div>
              <div>
                <span className="font-medium">Keyshare Attribute: </span>{" "}
                {env.keyshare_attribute}
              </div>
              <div>
                <span className="font-medium">Contact Website: </span>{" "}
                <a
                  href={env.contact_website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {env.contact_website}
                </a>
              </div>
            </CardContent>
          </Card>
        ))}
    </div>
  );
}
