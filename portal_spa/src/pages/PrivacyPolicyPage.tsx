function PrivacyPolicyPage() {
  return (
    <div className="font-[family-name:var(--font-geist-sans)] container md:max-w-5xl mx-auto grid p-4 gap-4 text-justify">
      <h1 className="text-2xl sm:text-4xl font-bold">Privacy</h1>
      <p className="font-bold">
        Your privacy is extremely important to us. We strictly adhere to all
        relevant privacy laws and regulations, ensuring your information is kept
        safe and handled with care. In this privacy statement, we explain what
        information we collect, how we use it, and your rights regarding your
        data. If you have any questions, or would like to know exactly what
        information we hold about you, please contact us.
      </p>

      <div className="grid gap-8">
        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">Privacy Statement</h3>
          <p className="text-sm">First version authored 1st of July 2025</p>
          <div>
            <p>
              The Yivi portal is software by Yivi B.V. (here in after referred
              to as ‘operators’) that uses the Yivi app for user authentication
              to provide services to organizations that want to participate in
              the Yivi ecosystem. For full details on how the Yivi app handles
              your personal data, please refer to the{" "}
              <a
                href="https://yivi.app/en/privacy/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                Yivi privacy statement
              </a>
              .
            </p>
            <p>
              The Yivi portal itself processes only the data necessary to
              support your organization’s registration and participation. Below,
              we explain what information is collected and how it is used by the
              portal.
            </p>
          </div>
        </div>

        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">
            What do the operators do with your data?
          </h3>
          <div>
            <p>
              The operators only collect and process data required for the
              operation and security of the Yivi Portal. This includes your
              email address for portal access, and phone number as a point of
              contact and your organization’s contact address, which are used
              solely to verify the legitimacy of portal registrations and to
              manage organizational accounts.
            </p>
          </div>
        </div>

        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">Legitimate basis</h3>
          <div>
            <p>
              When acting as a data controller, the operators have legitimate
              grounds for processing personal data in connection with Yivi: they
              have your consent, and processing is necessary for fulfillment of
              their agreement with you. We process personal data only to ensure
              the essential functions of the portal, such as registration,
              verification, and secure access for your organization.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PrivacyPolicyPage;
