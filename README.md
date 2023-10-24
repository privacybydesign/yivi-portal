# Yivi Portal
The Yivi Portal is a web application for managing registrations for the [Yivi scheme](https://irma.app/docs/schemes/) of the [Yivi ecosystem](https://irma.app/docs/what-is-irma/).
Verifiers and issuers can register themselves in the Yivi scheme via the portal and manage their registration.

Specifically, Yivi Portal should make it easy to manage the schemes that are currently managed in the following repositories:
- [pbdf](https://github.com/privacybydesign/pbdf-schememanager)
- [pbdf-requestors](https://github.com/privacybydesign/pbdf-requestors)
- [irma-demo](https://github.com/privacybydesign/irma-demo-schememanager)
- [irma-demo-requestors](https://github.com/privacybydesign/irma-demo-requestors)

> Yivi is formerly called IRMA and is currently being rebranded. As such, some of the documentation still refers to IRMA.

## Functionality

### Registration
Organizations can be registered in the Yivi portal after disclosure of valid [KvK credentials (via Yivi)](https://privacybydesign.foundation/attribute-index/nl/pbdf.signicat.kvkTradeRegister.html) by an authorized representative of the organization.

> **To be discussed**: 
> 
> Perhaps, for legal reasons, the registration should be done with a Yivi signature, instead of a Yivi disclosure.

After registration, the organization can enter the email addresses of people that are authorized to access the portal on behalf of the organization.
This way, the organization can manage its own users without requiring them to be actual legal representatives of the organization.

When a user logs in (by disclosing their email address via Yivi) to the portal, they can see a list of all organizations they have access to in the portal.

### Scheme management
The Yivi Portal can manage multiple Yivi schemes.
There are two types of schemes:
- issuer schemes that contain credential definitions and issuers
- requestor schemes that contain verifiers

Apart from that, a scheme can be a demo scheme or a production scheme.
Demo schemes are used for testing and development purposes. 
Production schemes are used for actual production.
Only after approval, a registration will be included in a production scheme.

#### Scheme export and signing
For security reasons, the Yivi Portal does not sign the scheme itself, as it should not possess the keys to do so.
Instead, the portal only _exports_ the scheme in the format that is required by [irmago](https://github.com/privacybydesign/irmago).
Signing the scheme should be done by the [irma command line application](https://irma.app/docs/schemes/#updating-and-signing-schemes-with-irma).

This should be done periodically to ensure that the scheme is up-to-date, but remains a manual action.

> It is yet to be determined how often this should be done and what guarantees we can give parties on how fast the scheme is updated.

#### Scheme hosting and distribution
> **To be discussed**:
> 
> The Yivi portal should know exactly which schemes are published.
> The Yivi portal can host the scheme itself for distribution, but it is also possible to host the scheme by a separate application.
> In the latter case, the Yivi Portal should monitor and download the scheme that is actually being published.

#### Approval process and status
The portal should display the current status of the registration in the scheme.

For a _demo_ scheme, the status can be one of the following:
- `draft`: the verifier or issuer is still working on their registration and will not be published.
- `ready`: the verifier or issuer has finished their registration and is ready to be published.
- `published`: the registration has been published in the scheme.

For a _production_ scheme, the status can be one of the following:
- `draft`: the verifier or issuer is still working on their registration, and it is not yet ready for review.
- `ready`: the verifier or issuer has finished their registration and is ready for review by the scheme manager.
- `approved`: the registration has been approved by the scheme manager and is ready to be published in the scheme.
- `rejected`: the registration has been rejected by the scheme manager and the verifier or issuer should make changes to their registration.
- `published`: the registration has been published in the scheme.

When a verifier changes their registration, the status is set to `draft` again.
The transition from `draft` to `ready` is a manual action by the verifier or issuer themselves.
The transition from `ready` to `approved` or `rejected` in production schemes is a manual action by the scheme manager.
The transition from `approved` to `published` in production schemes, or from `ready` to `published` in demo schemes, is an automated action by the portal, based on monitoring of the published schemes (see above).

### Verifier portal
An organization can register itself as a [(pretty) verifier](https://creativecode.github.io/irma-made-easy/posts/pretty-verifier-names/) in a requestor scheme via the portal.
Here, they can upload a small logo and their display name (and potentially other information that will be required for the scheme).

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

### Issuer portal
For future work. The Yivi Portal can also be used to register issuers and their credentials (and public keys).

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
The purpose of the Yivi Portal is to make it easy for verifiers to register themselves in the Yivi scheme and become a pretty verifier.
In the future, the Yivi mobile app can be configured to display warnings when a verifier is not registered in the Yivi scheme.
This way, the Yivi Portal can help to prevent over-asking in the Yivi ecosystem and make it easier for users to trust verifiers.