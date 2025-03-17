from django.core.management.base import BaseCommand
from portal_backend.crons import (
    NewDNSVerification,
    ExistingDNSVerification,
    TrustedAPsImport,
    TrustedRPsImport,
)


class Command(BaseCommand):
    help = "Run specific cron job"

    def add_arguments(self, parser):
        parser.add_argument("job_name", type=str, help="Name of the cron job to run")

    def handle(self, *args, **options):
        job_name = options["job_name"]
        jobs = {
            "new_dns": NewDNSVerification,
            "existing_dns": ExistingDNSVerification,
            "trusted_aps": TrustedAPsImport,
            "trusted_rps": TrustedRPsImport,
        }

        if job_name in jobs:
            job = jobs[job_name]()
            self.stdout.write(f"Running job: {job_name}")
            job.do()
            self.stdout.write(self.style.SUCCESS(f"Successfully ran {job_name}"))
        else:
            self.stdout.write(self.style.ERROR(f"Job {job_name} not found"))
