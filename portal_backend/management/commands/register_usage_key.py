from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from portal_backend.models.models import Organization
from portal_backend.services import usage


class Command(BaseCommand):
    help = (
        "Register the usage reporting public key of a Yivi server for an organization. "
        "The server prints the key with `irma server usage-key`."
    )

    def add_arguments(self, parser):
        parser.add_argument("org_slug", type=str, help="Slug of the organization")
        parser.add_argument(
            "public_key_file", type=str, help="PEM file with the public key"
        )
        parser.add_argument("--label", type=str, default="", help="Label of the key")

    def handle(self, *args, **options):
        try:
            organization = Organization.objects.get(slug=options["org_slug"])
        except Organization.DoesNotExist as e:
            raise CommandError(f"Unknown organization {options['org_slug']}") from e
        with open(options["public_key_file"], encoding="utf-8") as f:
            pem = f.read()
        try:
            server_key = usage.register_key(organization, pem, options["label"])
        except ValueError as e:
            raise CommandError(str(e)) from e
        except IntegrityError as e:
            raise CommandError("This key is already registered") from e
        self.stdout.write(
            f"Registered key {server_key.thumbprint} for {organization.slug}"
        )
