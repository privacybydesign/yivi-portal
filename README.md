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

### Running the Frontend

```bash
cd portal_frontend
npm install
npm run dev
```

### Running the Backend

Build and run with Docker. Currently, migrations are in the gitignore list due to ongoing restructuring of the model. This means migrations will be made and then applied for you.

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
```

Then start the services:

```bash
docker compose up -d
```

Since the database will be empty, you can populate it with test data:

```bash
docker compose exec yivi-portal python manage.py create_test_data
```

### Admin Access

The easiest way to view the database is with Django admin. You will need a superuser:

```bash
docker compose exec yivi-portal python manage.py createsuperuser
```

**Note!** If changes are made to the model, please record it in the ER diagram `dbrelations.md`.

**Note!** If you are testing endpoints with permission class `IsAuthenticated`, you first need to run the frontend project, login with Yivi (currently bound to Yivi staging server), and obtain the token.

### Service URLs

* Backend API: http://localhost:8000/
* Frontend: http://localhost:3000/
* Admin panel: http://localhost:8000/admin/

## API Documentation

API documentation is available at:
* Swagger UI: `/swagger/`
* ReDoc: `/redoc/`

## Available Endpoints

| **Endpoint**                                                                                                     | **Method** | **Description**                                                      |
|------------------------------------------------------------------------------------------------------------------|------------|----------------------------------------------------------------------|
| **Organizations**                                                                                                           |                                                                      |
| `/v1/organizations/`                                                                                            | `GET`      | List all organizations                                               |
| `/v1/organizations/<uuid:pk>/`                                                                                  | `GET`      | Retrieve details of a specific organization                          |
| `/v1/organizations/<uuid:pk>/maintainers/`                                                                      | `GET`      | List maintainers of a specific organization                          |
| `/v1/organizations/<uuid:pk>/register-rp/`                                                                      | `POST`     | Register the organization as a relying party (RP)                   |
| **Trust Models**                                                                                                |           |                                                                      |
| `/v1/trust-models/`                                                                                             | `GET`      | List all trust models                                                |
| `/v1/trust-models/<str:name>/`                                                                                  | `GET`      | Retrieve details of a specific trust model                           |
| `/v1/trust-models/<str:name>/environments/`                                                                     | `GET`      | List all environments within a specific trust model                  |
| `/v1/trust-models/<str:name>/environments/<str:environment>/`                                                   | `GET`      | Retrieve details of a specific environment within a trust model      |
| **Public Listings in a Trust Model Environment**                                                                |           |                                                                      |
| `/v1/trust-models/<str:name>/environments/<str:environment>/organizations/`                                     | `GET`      | List organizations in a trust model environment                      |
| `/v1/trust-models/<str:name>/environments/<str:environment>/attestation-providers/`                             | `GET`      | List attestation providers (APs) in a trust model environment        |
| `/v1/trust-models/<str:name>/environments/<str:environment>/relying-parties/`                                   | `GET`      | List relying parties (RPs) in a trust model environment              |
| **Relying Parties**                                                                                                        |                                                                      |
| `/v1/relying-party/<str:slug>/hostname-status/`                                                               | `GET`      | Get hostname validation status of a relying party                    |
| `/v1/relying-party/<str:slug>/registration-status/`                                                           | `GET`      | Get registration status of a relying party                           |
| **Yivi Authentication**                                                                                          |          |                                                                      |
| `/v1/session/`                                                                                                  | `POST`     | Start a new Yivi authentication session                              |
| `/v1/token/<str:token>/`                                                                                        | `GET`      | Retrieve authentication token from the Yivi session                  |

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

### Issuer Registration
(in progress...)

### AP and RP List up to date with the scheme 
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

he Yivi Portal was built as based on recommendations in the [master thesis of Job Doesburg](https://jobdoesburg.nl/docs/Measures_against_over_asking_in_SSI_and_the_Yivi_ecosystem.pdf). Later, the Yivi Team started their own fork of this project to make it appropriate for production.