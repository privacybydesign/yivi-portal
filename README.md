# Yivi Portal

Yivi Portal is a project designed to streamline the process of joining Yivi as an Issuer or Verifier, with an outlook toward adopting EUDI Wallet terminologies. Relying Parties can use the protal to join the Trusted Verifier Program of Yivi.


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
* **Frontend**: React
* **Database**: PostgreSQL
* **Authentication**: Yivi authentication

The project consists of two main components:
1. **Portal Backend**: Django application with REST API
2. **Portal Frontend**: React single page application

## Development Setup


### Running the Project

Build and run the project with Docker. To check for unapplied migrations do 
`docker compose exec django python manage.py makemigrations`. If you have any unapplied migrations do `docker compose exec django python manage.py migrate`

Create a `.env` file using `.env.sample`

Then start the services:

```bash
docker compose up --build
```
Then run `docker compose exec django python manage.py run_crons trusted_aps` first and then `docker compose exec django python manage.py run_crons trusted_rps`

This imports the Attestation Providers and Relying Parties from the Yivi schemes. This will also run by itself at each cronjob interval set in the `portal_backend/crons.py`

### Admin Access

The easiest way to view the database is with Django admin. You will need a superuser:

```bash
docker compose exec django python manage.py createsuperuser
```
Then access with your credentials at `http://{host}:8000/admin/`

### Run Django Tests

To run the tests in portal_backend/tests, use this command:

```bash
docker compose exec django python manage.py test
```

### Cronjobs

Currently, 3 types of  cronjobs are set. `DNS Verification`, `Import Trusted RPs`, `Import Trusted APs`. The latter two use appropriate scheme repositories to create or update entities in the database.

## Acknowledgements

The Yivi Portal was built as based on recommendations in the [master thesis of Job Doesburg](https://jobdoesburg.nl/docs/Measures_against_over_asking_in_SSI_and_the_Yivi_ecosystem.pdf). Later, the Yivi Team started their own fork of this project to align it with European Standards such as EUDI Wallet ARF, while making the project production-ready.
