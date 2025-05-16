function TermsOfServicePage() {
  return (
    <div className="font-[family-name:var(--font-geist-sans)] container md:max-w-5xl mx-auto grid p-4 gap-4 text-justify">
      <h1 className="text-2xl sm:text-4xl font-bold">Terms of service</h1>
      <p className="font-bold">
        When you visit our site, you agree to our site terms and conditions.
      </p>

      <div className="grid gap-8">
        <div className="grid gap-4">
          <h3 className="text-xl sm:text-3xl font-bold">
            Site terms and conditions:
          </h3>
          <div>
            <p>
              <ul>
                <li>
                  We are not liable for damages resulting from errors on our
                  site.
                </li>
                <li>
                  We own all content (text/image) on our site unless we state
                  otherwise. You may save, copy or distribute content from our
                  site. Please mention us as source.
                </li>
                <li>
                  Our terms and conditions are governed by Dutch law. Do you
                  disagree? Submit it to a competent court in Arnhem.
                </li>
              </ul>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TermsOfServicePage;
