from django.core.management.base import BaseCommand

from portal_backend.models.models import Scheme
from portal_backend.published_check import fetch_requestor_scheme


class Command(BaseCommand):
    """Generate a requestor scheme based on the entries in the portal database"""

    def add_arguments(self, parser):
        parser.add_argument(
            "scheme_id",
            type=str,
            help="The scheme ID to use",
        )
        parser.add_argument(
            "--create",
            action="store_true",
            dest="create",
            default=False,
            help="Create verifiers that do not exist yet",
        )

    def handle(self, *args, **options):
        scheme_id = options["scheme_id"]
        scheme = Scheme.objects.get(id=scheme_id, scheme_type=Scheme.REQUESTOR)
        fetch_requestor_scheme(scheme, create_verifiers=options["create"])
