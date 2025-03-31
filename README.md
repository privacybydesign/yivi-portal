# Yivi Portal

Yivi Portal is a project designed to streamline the process of joining Yivi as an Issuer or Verifier, with an outlook toward adopting EUDI Wallet terminologies. Relying Parties can use the protal to join the Trusted Verifier Program of Yivi.

**Note!** This is a work in progress. Feel free to contribute.

## Terminology Mapping

Yivi terminology is translated to the following in the scope of this project:

| Yivi Term | Project Term |
|-----------|--------------|
| **Issuer** | Attestation Provider |
| **Verifier** | Relying Party |
| **Scheme** | Trust Model Environment (for either Attestation Providers or Relying Parties) |
| **pbdf** | Trust model production environment for Attestation Providers |
| **pbdf staging** | Trust model development environment for Attestation Providers |
| **irma-demo** | Trust model demo environment for Attestation Providers |
| **requestors scheme** | Trust model production environment for Relying Parties |

## Project Architecture

This project is built with:

* **Backend**: Django REST framework (Python)
* **Frontend**: Next.js (React, TypeScript)
* **Database**: PostgreSQL
* **Authentication**: Yivi authentication

The project consists of two main components:
1. **Portal Backend**: Django application with REST API
2. **Portal Frontend**: Next.js application with React components

## Development Setup


### Running the Project

Build and run the project with Docker. This will also build the frontend application.
Currently, migrations are in the gitignore list due to ongoing restructuring of the model. This means migrations will be made and then applied for you.

#### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
YIVI_SERVER_URL=https://yivi.example.nl
YIVI_SERVER_TOKEN=token-used-in-irma-server
POSTGRES_USER=yivi
POSTGRES_PASSWORD=yivi
POSTGRES_DB=yivi
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost
AP_ENV=production
RP_ENV=production
```

Then start the services:

```bash
docker compose up -d
```

Since the database will be empty, you can populate it with test data:

```bash
docker compose exec django python manage.py create_test_data
```

### Admin Access

The easiest way to view the database is with Django admin. You will need a superuser:

```bash
docker compose exec django python manage.py createsuperuser
```

**Note!** If changes are made to the model, please record it in the ER diagram `dbrelations.md`.

**Note!** If you are testing endpoints with permission class `IsAuthenticated`, you first need to run the frontend project, login with Yivi (currently bound to Yivi staging server), and obtain the token. Currently the token is set to be valid for a day.

### Service URLs

* Backend API: http://localhost:8000/
* Frontend: http://localhost:9000/
* Admin panel: http://localhost:8000/admin/


## Available Endpoints

| **Endpoint**                                                                                                     | **Method** | **Description**                                                      |
|------------------------------------------------------------------------------------------------------------------|------------|----------------------------------------------------------------------|
| **API Documentation**                                                                                             |            |                                                                      |
| `/swagger<format>/`                                                                                               | `GET`      | Retrieve the raw OpenAPI schema (JSON/YAML)                          |
| `/swagger/`                                                                                                       | `GET`      | Interactive Swagger UI for API documentation                         |
| `/redoc/`                                                                                                         | `GET`      | ReDoc UI for API documentation                                       |
| **Organizations**                                                                                                 |            |                                                                      |
| `/v1/organizations/`                                                                                         | `GET`      | List all organizations                                               |
| `/v1/organizations/<str:org_slug>/`                                                                          | `GET`      | Retrieve details of a specific organization                          |
| `/v1/organizations/<str:org_slug>/maintainers/`                                                              | `GET`      | List maintainers of a specific organization                          |
| **Relying Parties**                                                                                               |            |                                                                      |
| `/v1/yivi/organizations/<str:org_slug>/relying-party/`                                                            | `POST`     | Register a new relying party (RP) for the organization               |
| `/v1/yivi/organizations/<str:org_slug>/relying-party/<str:environment>/<str:rp_slug>/`                            | `GET`      | Retrieve details of a relying party (RP) in a specific environment   |
| `/v1/yivi/organizations/<str:org_slug>/relying-party/<str:rp_slug>/`                                              | `PUT`      | Update details of a relying party (RP)                               |
| `/v1/yivi/organizations/<str:org_slug>/relying-party/<str:environment>/<str:rp_slug>/dns-verification/`           | `GET`      | Get DNS verification status for a relying party (RP) hostname        |
| **Trust Models**                                                                                                  |            |                                                                      |
| `/v1/trust-models/`                                                                                               | `GET`      | List all trust models                                                |
| `/v1/trust-models/<str:name>/`                                                                                    | `GET`      | Retrieve details of a specific trust model                           |
| `/v1/<str:name>/environments/`                                                                                    | `GET`      | List all environments within a specific trust model                  |
| `/v1/<str:trustmodel_name>/<str:environment>/`                                                                    | `GET`      | Retrieve details of a specific environment within a trust model      |


## Testing API Endpoints
As the front-end is still in development, you can import `postman-collection.json` in Postman, to easily test endpoints and format of data they return.

## Features

### Organization Registration
* Organizations register by filling in the registration form (TODO: Authentication needed)
* Update of organization profiles, logos, and contact information
* A maintainer can add new maintainers

### Relying Party Registration
* Registration as a Verifier (Relying Party) in a Yivi scheme
* Automatic DNS verification for Relying Party hostnames
* Disclosure request registration:
   * With choice from credentials from existing Attestation Providers
   * Purpose inquiry per Condiscon (session request format of Yivi) and per individual chosen attributes

### Cron Jobs

Currently, 3 types of Cron Jobs are set. `DNS Verification`, `Import Trusted RPs`, `Import Trusted APs`. The latter use appropriate scheme repositories to create or update entities in the database.

### AP Registration
(in progress...)


### Status Tracking
The state of AP or RP registrations from an organization can be followed with status detailed workflow:
* **Draft**: Organization is working on their registration
* **Ready/Pending for Review**: Registration is complete and ready for review
* **Approved**: Registration has been approved by Yivi admins (production only)
* **Rejected**: Registration has been rejected and requires changes
* **Published**: Registration has been published in the scheme
* **Invalidated**: Registration has become invalid and needs fixes

## Acknowledgements

The Yivi Portal was built as based on recommendations in the [master thesis of Job Doesburg](https://jobdoesburg.nl/docs/Measures_against_over_asking_in_SSI_and_the_Yivi_ecosystem.pdf). Later, the Yivi Team started their own fork of this project to make it appropriate for production.