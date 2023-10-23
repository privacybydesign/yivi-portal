import json

from django.core.management.base import BaseCommand

from schememanager.models import Verifier, Scheme


def serialize_verifier(verifier: Verifier) -> dict:
    return {
        "id": f"{verifier.scheme}.{verifier.id}",
        "name": {
            "nl": verifier.name_nl,
            "en": verifier.name_en,
        },
        "logo": verifier.logo.name if verifier.logo else None,
        "hostnames": [
            hostname.hostname for hostname in verifier.verifierhostname_set.all()
        ],
        "scheme": verifier.scheme.id,
    }


class Command(BaseCommand):
    """Generate a requestor scheme based on the entries in the portal database"""

    def add_arguments(self, parser):
        parser.add_argument(
            "scheme_id",
            type=str,
            help="The scheme ID to use",
        )
        parser.add_argument(
            "--include-unaccepted",
            action="store_true",
            dest="include-unaccepted",
            default=False,
            help="Include unaccepted verifiers in the scheme",
        )

    def handle(self, *args, **options):
        scheme_id = options["scheme_id"]
        scheme = Scheme.objects.get(id=scheme_id, scheme_type=Scheme.REQUESTOR)
        verifiers = Verifier.objects.filter(scheme=scheme)
        if not options["include-unaccepted"]:
            verifiers = verifiers.filter(accepted=True)
        data = [serialize_verifier(verifier) for verifier in verifiers]
        scheme_data = json.dumps(data, indent=2)
        self.stdout.write(scheme_data)
