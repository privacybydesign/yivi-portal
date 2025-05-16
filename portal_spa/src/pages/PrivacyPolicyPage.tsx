function PrivacyPolicyPage() {
  return (
    <div className="font-[family-name:var(--font-geist-sans)] container md:max-w-5xl mx-auto grid p-4 gap-4 text-justify">
      <h1 className="text-2xl sm:text-4xl font-bold">Privacy</h1>
      <p className="font-bold">
        Your privacy is very important to us. We therefore adhere to privacy
        legislation. This means that your information is safe with us and that
        we handle it properly. In this privacy statement, we explain everything
        we do with the information we collect about you. If you have any
        questions, or want to know exactly what we track about you, please
        contact us.
      </p>

      <div className="grid gap-8">
        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">
            Yivi Privacy Statement
          </h3>
          <div>
            <p>
              <strong>Version November 1, 2024</strong>
            </p>
            <p>
              The Privacy by Design Foundation and Caesar Groep (hereafter: the
              administrators) process personal data for the purpose of achieving
              attribute-based authentication and signing via the system Yivi.
              The administrators are responsible for the processing and consider
              your privacy very important. They therefore comply with privacy
              legislation. This means that your data is safe with them and that
              they handle it properly.
            </p>
            <p>
              The design of Yivi is such that personal data, in the form of
              attributes, are stored encrypted exclusively with the user in the
              Yivi app on their own phone or tablet and that the user has
              control over who they share their personal data with.
            </p>
            <p>
              Attributes are a small piece of data that usually contains a
              statement about the owner of the attribute (e.g., “&gt; 18
              years”). An attribute is, for example, your bank account number,
              name, home address, e-mail address, 06 number or Citizen Service
              Number (BSN). No one, including administrators, can see from which
              attribute publisher the user retrieves attributes or with whom the
              user shares their attributes. Nor can anyone see which attributes
              are retrieved or shared by the user. Retrieved attributes can be
              accessed and shared only through the Yivi app. The entire system
              is based on privacy by design.
            </p>
            <p>
              The purpose of Yivi is to allow secure and confidential, data
              minimization-based login, access, consent and signature with
              third-party authentication processes through Yivi.
            </p>
          </div>
        </div>

        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">
            What do the administrators do with your data?
          </h3>
          <div>
            <p>
              Below you can read what the administrators do with the data they
              collect from you through Yivi.
            </p>
            <p>
              When registering new Yivi users, the administrators store for each
              user only a random username (the app ID) and, only if the user
              provides it himself, an e-mail address. In addition, they store a
              very limited collection of historical usage data, as described in
              more detail below.
            </p>
          </div>
        </div>

        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">Basis</h3>
          <div>
            <p>
              The legal bases for the processing by administrators as
              controllers, in the context of Yivi, are consent of the data
              subject and necessary for the performance of the user agreement.
              The processing of personal data by administrators is necessary to
              ensure the functionalities of Yivi and the operation of the app.
              For example, the processing of the mobile number, email address as
              an attribute, the app ID and historical usage data is necessary
              for the verification and operation of the app. Thus, the
              processing is necessary for the performance of the agreement
              between the administrators and the user of the Yivi app.
            </p>
            <p>
              In addition, if the user chooses to use the recovery function, by
              passing the email address, the user explicitly authorizes the
              administrators to have the recovery email address processed.
            </p>
            <p>
              Incidentally, the Yivi app also explicitly asks the user for
              permission for this action with each receipt and with each
              disclosure of attributes. This constitutes the basis for the
              processing of the concerning attributes by these (third) parties.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PrivacyPolicyPage;
