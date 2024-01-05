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
The Yivi portal does not host or distribute the schemes itself, but monitors the published version.

#### Approval process and status
The portal should display the current status of the registration in the scheme.

For a _demo_ scheme, the status can be one of the following:
- `draft`: the verifier or issuer is still working on their registration and will not be published.
- `ready`: the verifier or issuer has finished their registration and is ready to be published.
- `published`: the registration has been published in the scheme.
- `invalidated`: the registration became invalid (e.g. because the hostname no longer verifies) and will be removed from the scheme on the next update.

For a _production_ scheme, the status can be one of the following:
- `draft`: the verifier or issuer is still working on their registration, and it is not yet ready for review.
- `ready`: the verifier or issuer has finished their registration and is **under review** by the scheme manager.
- `approved`: the registration has been approved by the scheme manager and is ready to be published in the scheme.
- `rejected`: the registration has been rejected by the scheme manager and the verifier or issuer should make changes to their registration.
- `published`: the registration has been published in the scheme.
- `invalidated`: the registration became invalid (e.g. because the hostname no longer verifies) and will be removed from the scheme on the next update.

When a verifier changes their registration, the status is set to `draft` again.
The transition from `draft` to `ready` is a manual action by the verifier or issuer themselves.
The transition from `ready` to `approved` or `rejected` in production schemes is a manual action by the scheme manager.
The transition from `approved` to `published` in production schemes, or from `ready` to `published` in demo schemes, is an automated action by the portal, based on monitoring of the published schemes (see above).
The transition from `published` to `invalidated` or `approved` to `invalidated` is an automated action by the portal as well.

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
For each attribute in the _condiscon_, the verifier should list the reason why they want to request the attribute (explanation for purpose binding) in both Dutch and English.
These explanations should clarify that indeed, the disclosure request is minimal.

### Issuer portal
For future work. The Yivi Portal can also be used to register issuers and their credentials (and public keys).

### Billing
> **For future work**
> 
> Verifiers should be able to classify themselves as a `small` / `medium` / `large` verifier in the portal (based on number of verifications per month).
> This classification is used to determine the billing of the verifier.

### Logging
For future work. Perhaps, the Yivi app should stochastically log disclosure sessions to the Yivi Portal, so that the portal can monitor the usage of the scheme and determine if verifiers are properly classified (see billing).
Probably, the logging should be a different microservice, as it should not be part of the portal itself.

## Technical specifications
The Yivi Portal is written in Python 3.11 and uses [the Django framework](https://www.djangoproject.com).
It can be run in a Docker container, for which a Dockerfile and docker-compose file are provided.
For the actual Yivi authentication, the portal communicates with a Yivi server that is running in a separate container.

### Development
1. Clone the repository
2. Make sure you have [Python 3.11](https://www.python.org/downloads/) installed. 
3. Make sure you have [Poetry](https://python-poetry.org) installed.
4. Install the dependencies with Poetry: 
    ```bash
    poetry install
    ```
5. Run the migrations:
    ```bash
    poetry run python manage.py migrate
    ```
6. Create an admin user:
    ```bash
    poetry run python manage.py createsuperuser --email <email> --username <username> --noinput
    ```
   We don't set up a password here, because we want to use Yivi authentication.
   If you want to use a password as fallback (to use Django admin login flow), that is possible as well.
7. Run the development server:
    ```bash
    poetry run python manage.py runserver
    ```

**Make sure to use the `yivi_portal.settings.development` settings module when running the development server.**

Also, a Yivi server should be available somewhere, for which the URL should be configured in the `YIVI_SERVER_URL` and the `YIVI_SERVER_TOKEN` environment variable.

### Deployment
For production deployment, the Dockerfile and docker-compose file can be used.

#### Docker image
The Dockerfile is based on the [official Python image](https://hub.docker.com/_/python) and installs the required dependencies.
It copies the source code into the image and sets the `yivi_portal.settings.production` settings module as the default settings module.
The `DJANGO_STATIC_ROOT` and `DJANGO_MEDIA_ROOT` environment variables are set to `/app/static` and `/app/media` respectively during the build.
During build, the static files are collected to the `DJANGO_STATIC_ROOT` directory, which is served by the webserver.

##### Webserver
The Docker images uses [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) as the webserver.
The uWSGI configuration is set in the `start.sh` script, which is the default command of the Docker image.

During startup, the `start.sh` script first runs the migrations.
The uWSGI configuration uses the `yivi_portal.wsgi` module as the WSGI module and to serve the static files from the `DJANGO_STATIC_ROOT` directory (which is set to `/app/static` during build) and the media files from the `DJANGO_MEDIA_ROOT` directory (which is set to `/app/media` during build).
This is done at the `DJANGO_STATIC_URL` and `DJANGO_MEDIA_URL` respectively, which are set to `/static/` and `/media/` during build by default, but can be overridden by setting the `DJANGO_STATIC_URL` and `DJANGO_MEDIA_URL` environment variables for runtime.
The webserver is exposed internally on port `8000` and runs with 4 workers and 2 threads (by the user `nobody` in the `nogroup` group).

##### Database
The production image expects a PostgreSQL database to be available.
The database connection is configured in the `yivi_portal.settings.production` settings module, using the `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD` environment variables.

##### Yivi server
Similar to during development, a Yivi server should be available somewhere, for which the URL should be configured in the `YIVI_SERVER_URL` and the `YIVI_SERVER_TOKEN` environment variable.

##### Expected environment variables
During runtime, the following environment variables are expected:
- `DJANGO_SECRET_KEY`: the secret key of the Django application
- `DJANGO_ALLOWED_HOSTS`: a comma-separated list of allowed hosts
- `POSTGRES_HOST`: the hostname of the PostgreSQL database
- `POSTGRES_PORT`: the port of the PostgreSQL database
- `POSTGRES_DB`: the name of the PostgreSQL database
- `POSTGRES_USER`: the username of the PostgreSQL database
- `POSTGRES_PASSWORD`: the password of the PostgreSQL database
- `YIVI_SERVER_URL`: the URL of the Yivi server (for all Yivi sessions)
- `YIVI_SERVER_TOKEN`: the token of the Yivi server (for all Yivi sessions)

Additionally, the following environment variables can be set:
- `DJANGO_STATIC_URL`: the URL where the static files are served from (default: `/static/`)
- `DJANGO_MEDIA_URL`: the URL where the media files are served from (default: `/media/`)

#### Docker-compose
An example docker-compose file is provided to run the Yivi Portal in production.

This file expects a [nginx reverse proxy](https://hub.docker.com/r/nginxproxy/nginx-proxy) to be running on the host machine, which proxies the requests to the Yivi Portal, based on the `VIRTUAL_HOST` environment variable, and automatically requests and renews TLS certificates using [Let's Encrypt](https://letsencrypt.org).

The docker-compose file starts 3 services:
- `yivi-portal`: the Yivi Portal itself
- `yivi-portal-db`: the PostgreSQL database that is used by the portal
- `yivi-portal-yivi`: the Yivi server that is used by the portal for Yivi sessions

The nginx reverse proxy should be providing the `web` network in Docker, which the Yivi Portal and Yivi server connect to.
Additionally, there is an internal `db` network, which is used by the Yivi Portal and the Yivi server to connect to the database.

The database data and the media files are stored in a Docker volumes `postgres-data` and `portal-media`.

In the docker-compose file, all hostnames are currently hardcoded, but they should be changed to the actual hostnames.
Additionally, secret information should be provided in a `.env` file, which should look like this:

```bash
YIVI_SERVER_URL=https://yivi.jobdoesburg.nl
YIVI_SERVER_TOKEN=test-yivi-token-1234
POSTGRES_USER=yivi
POSTGRES_PASSWORD=yivi
POSTGRES_DB=yivi
DJANGO_SECRET_KEY=secret-key
```

##### Useful commands
Run the following command to create an admin user:
```bash
docker-compose exec yivi-portal python manage.py createsuperuser --email <email> --username <username> --noinput
```
Note that a user must re-login before the admin interface is available.


## More information
The Yivi Portal is built as based on recommendations in the [master thesis of Job Doesburg](https://jobdoesburg.nl/docs/Measures_against_over_asking_in_SSI_and_the_Yivi_ecosystem.pdf).
The purpose of the Yivi Portal is to make it easy for verifiers to register themselves in the Yivi scheme and become a pretty verifier.
In the future, the Yivi mobile app can be configured to display warnings when a verifier is not registered in the Yivi scheme.
This way, the Yivi Portal can help to prevent over-asking in the Yivi ecosystem and make it easier for users to trust verifiers.
