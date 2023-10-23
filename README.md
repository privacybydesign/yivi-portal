# Yivi Portal
The Yivi Portal is a place where issuers and (pretty) verifiers can register themselves in the Yivi scheme.

## Functionality

### Registration
Organizations can be registered in the Yivi portal after disclosure of valid [KvK credentials (via Yivi)](https://privacybydesign.foundation/attribute-index/nl/pbdf.signicat.kvkTradeRegister.html) by an authorized representative of the organization (or perhaps, it should be a signature).

After registration, the organization can enter email addresses of people that are authorized to access the portal on behalf of the organization.
This way, the organization can manage its own users without requiring them to be actual legal representatives of the organization.

When a user logs in (by disclosing their email address via Yivi) to the portal, they can see a list of all organizations they have access to in the portal.

### Verifier portal
An organization can register itself as a (pretty) verifier in the Yivi scheme via the portal.
Here, they can upload a small logo and their display name (and potentially other information that will be required for the scheme).

The portal should display the current status of the verifier's registration in the scheme (e.g. draft, review-requested, approved, rejected, published).
- Draft: the verifier is still working on their registration and it is not yet ready for review.
- Review-requested: the verifier has finished their registration and is ready for review by the scheme manager.
- Approved: the verifier has been approved by the scheme manager and is ready to be published in the scheme.
- Rejected: the verifier has been rejected by the scheme manager and should make changes to their registration.
- Published: the verifier has been published in the scheme.

When a verifier changes their registration, the status should be set to draft again.
When the verifier is ready for review, they can request a review by the scheme manager.
Meanwhile, the old registration will still be published in the scheme, until a new scheme is published.

The Yivi portal monitors the currently published scheme and keeps track of the verifier's registration in the scheme.

#### Hostname registration 
Verifiers can register the hostnames of their Yivi servers.
This hostname is used to identify the verifier in the Yivi scheme.
After entering a hostname of a Yivi server, the Yivi Portal creates a DNS challenge.
The verifier should add a DNS TXT record to the DNS zone of the hostname that is registered in the portal.
In the background (e.g. every 15 minutes), the portal checks if the DNS TXT record is added and if it is valid.
If the DNS TXT record is valid, the hostname will be successfully registered in the scheme.

In the background, the portal will check periodically if the DNS TXT records are still valid.
If the DNS TXT record is not valid anymore, the hostname will be removed from the scheme and the verifier will be notified.

#### Disclosure request registration
Verifiers can register the disclosure requests they want to perform by submitting the [_condiscon_](https://irma.app/docs/condiscon/) of the disclosure request.
For each attribute in the _condiscon_, the verifier should specify the reason why they want to request the attribute.

Each registered disclosure request will be checked manually and approved before it will be included in the scheme.
As such, when a disclosure request is approved, it cannot be changed anymore.
When an organization wants to change a disclosure request, they should register a new disclosure request (and probably remove the old one).

### Issuer portal
For future work. The Yivi Portal can also be used to register issuers and their credentials (and public keys).

### Scheme management / export / signing
For security reasons, the Yivi Portal cannot sign the scheme itself, as it should not possess the keys to do so.
Instead, the portal can export the scheme in the format that is required by [irmago](https://github.com/privacybydesign/irmago).
Signing the scheme should be done by the [irma command line application](https://irma.app/docs/schemes/#updating-and-signing-schemes-with-irma).

This should be done periodically to ensure that the scheme is up-to-date.
It is yet to be determined how often this should be done and what guarantees we can give to verifiers on how fast the scheme is updated.

### Scheme hosting and distribution
For future work.
Perhaps, the Yivi Portal can also host the scheme (after it is signed) for all parties to download.

### Billing
For future work.

### Logging
For future work. Perhaps, the Yivi app should stochastically log disclosure sessions to the Yivi Portal, so that the portal can monitor the usage of the scheme.

## Technical specifications
The Yivi Portal is written in Python 3.11 and uses [the Django framework](https://www.djangoproject.com).
It can be run in a Docker container, for which a Dockerfile and docker-compose file are provided.
For the actual Yivi authentication, the portal communicates with a Yivi server that is running in a separate container.

## More information
The Yivi Portal is built as based on recommendations in the [master thesis of Job Doesburg](https://jobdoesburg.nl/docs/Measures_against_over_asking_in_SSI_and_the_Yivi_ecosystem.pdf).