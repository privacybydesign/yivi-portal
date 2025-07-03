import OrganizationForm from "@/components/forms/organization/OrganizationForm";
import { Link } from "react-router-dom";
import { useTranslation, Trans } from "react-i18next";

export default function RegisterOrganization() {
  const { t } = useTranslation();

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex flex-col gap-6 mb-6 bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-1">Register Organization</h1>
        <OrganizationForm
          pendingButtonLabel={t("generic.submitting")}
          submitButtonLabel={t("generic.submit")}
        ></OrganizationForm>
      </div>
      <div className="text-sm text-muted-foreground">
        {t("register_org_page.info")}
        <br />
        <br />
        <Trans i18nKey="register_org_page.already_member">
          If you are already part of Yivi's echosystem as listed
          <Link to="/organizations/">here</Link>, you will not need to fill this
          form again. Please contact us to be granted access and maintainer
          rights. You will receive an email once this has been processed.
        </Trans>
        <br />
        <br />
        <Trans i18nKey="register_org_page.contact">
          If you have any questions or need assistance, please contact us at
          <a href="mailto:support@yivi.app" className="text-blue-600">
            support@yivi.app
          </a>
          .
        </Trans>
      </div>
    </div>
  );
}
