# import json

# from django.core.management.base import BaseCommand

# from schememanager.models.scheme import Scheme
# from schememanager.models.verifier import Verifier


# class Command(BaseCommand):
#     """Generate a requestor scheme based on the entries in the portal database"""

#     def add_arguments(self, parser):
#         parser.add_argument(
#             "scheme_id",
#             type=str,
#             help="The scheme ID to use",
#         )

#     def handle(self, *args, **options):
#         scheme_id = options["scheme_id"]
#         scheme = Scheme.objects.get(id=scheme_id, scheme_type=Scheme.REQUESTOR)
#         verifiers = Verifier.objects.filter(
#             scheme=scheme, approved_scheme_data__isnull=False
#         )
#         data = [verifier.approved_scheme_data for verifier in verifiers]
#         scheme_data = json.dumps(data, indent=2)
#         self.stdout.write(scheme_data)
