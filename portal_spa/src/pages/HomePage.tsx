import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

function HomePage() {
  const { t } = useTranslation();
  return (
    <div className="flex justify-center items-start p-6">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start w-full max-w-3xl">
        <img
          className="dark:invert"
          src="/yivi-logo.svg"
          alt="Yivi logo"
          width={180}
          height={38}
        />
        <h1 className="text-2xl sm:text-4xl font-bold text-center sm:text-left">
          {t("welcome")}
        </h1>
        <p className="text-sm sm:text-base text-center sm:text-left">
          {t("explore")}
        </p>

        <div className="grid gap-4 sm:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>{t("join_ecosystem")}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col justify-between flex-1">
              {t("join_ecosystem_desc")}
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link to="/organizations/register">
                    {t("register_org")}
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>{t("ecosystem_card")}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col justify-between flex-1">
              {t("ecosystem_desc")}
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link to="/organizations">{t("view_orgs")}</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>{t("supported_credentials")}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col justify-between flex-1">
              {t("supported_credentials_desc")}
              <div className="mt-4">
                <Button variant="outline" asChild>
                  <Link to="/attribute-index">{t("view_attribute_index")}</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

export default HomePage;
