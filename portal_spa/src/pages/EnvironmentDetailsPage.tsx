import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { axiosInstance } from "@/services/axiosInstance";
import { getLocalizedField } from "@/utils/getLocalizedField";
import i18n from "@/i18n";
import { toast } from "sonner";
import type { YiviEnvironment } from "@/models/yivi-environment";
import { useParams } from "react-router-dom";
import { AxiosError } from "axios";
import { useTranslation } from "react-i18next";

export default function EnvironmentDetailsPage() {
  const { environment: currentEnv } = useParams();
  const [yiviEnvironments, setYiviEnvironment] = useState<YiviEnvironment[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  useEffect(
    () => window.scrollTo({ top: 0, behavior: "smooth" }),
    [currentEnv]
  );

  useEffect(() => {
    const fetchEnvironments = async () => {
      try {
        const response = await axiosInstance.get("/v1/yivi/environments/");
        setYiviEnvironment(response.data);
      } catch (error) {
        toast.error(t("generic.something_went_wrong"), {
          description:
            error instanceof AxiosError
              ? error.message
              : t("generic.try_again_later"),
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
          ? `${currentEnv.charAt(0).toUpperCase() + currentEnv.slice(1)} ${t(
              "environment.details"
            )}`
          : t("environment.all")}
      </h1>

      {loading && (
        <p className="text-muted-foreground">{t("environment.loading")}</p>
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
                <span className="font-medium">{t("environment.id")}: </span>
                {yiviEnv.scheme_id}
              </div>
              <div>
                <span className="font-medium">{t("environment.name")}: </span>
                {getLocalizedField(yiviEnv, "name", i18n.language)}
              </div>
              <div>
                <span className="font-medium">
                  {t("environment.description")}:{" "}
                </span>{" "}
                {getLocalizedField(yiviEnv, "description", i18n.language)}
              </div>
              <div>
                <span className="font-medium">{t("environment.url")}: </span>{" "}
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
                <span className="font-medium">
                  {t("environment.timestamp_server")}:{" "}
                </span>{" "}
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
                <span className="font-medium">
                  {t("environment.keyshare_server")}:{" "}
                </span>{" "}
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
                <span className="font-medium">
                  {t("environment.keyshare_website")}:{" "}
                </span>{" "}
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
                <span className="font-medium">
                  {t("environment.keyshare_attribute")}:{" "}
                </span>{" "}
                {yiviEnv.keyshare_attribute}
              </div>
              <div>
                <span className="font-medium">
                  {t("environment.contact_website")}:{" "}
                </span>{" "}
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
