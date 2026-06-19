from django.db import migrations


def add_bank_income_profile(apps, schema_editor):
    YiviTrustModelEnv = apps.get_model("portal_backend", "YiviTrustModelEnv")
    Organization = apps.get_model("portal_backend", "Organization")
    AttestationProvider = apps.get_model("portal_backend", "AttestationProvider")
    Credential = apps.get_model("portal_backend", "Credential")
    CredentialAttribute = apps.get_model("portal_backend", "CredentialAttribute")

    try:
        yivi_tme = YiviTrustModelEnv.objects.get(environment="demo")
    except YiviTrustModelEnv.DoesNotExist:
        return

    org, _ = Organization.objects.get_or_create(
        slug="VeriD",
        defaults={
            "name_en": "Demo Ver.ID",
            "name_nl": "Demo Ver.ID",
            "is_verified": True,
        },
    )

    ap, _ = AttestationProvider.objects.get_or_create(
        yivi_tme=yivi_tme,
        ap_slug="VeriD",
        defaults={
            "organization": org,
            "version": "4",
            "shortname_en": "Demo Ver.ID",
            "shortname_nl": "Demo Ver.ID",
            "contact_email": "demo@ver.id",
            "ready": True,
            "reviewed_accepted": True,
            "published": True,
        },
    )

    credential, _ = Credential.objects.get_or_create(
        attestation_provider=ap,
        credential_id="bankIncomeProfile",
        defaults={
            "name_en": "Demo Bank Income Profile",
            "name_nl": "Demo Bankrekening inkomensprofiel",
            "shortname_en": "Demo Bank Income Profile",
            "shortname_nl": "Demo Bankrekening inkomensprofiel",
            "description_en": "Bank account income profile from De Hollandsche Bank",
            "description_nl": "Bankrekening inkomensprofiel van De Hollandsche Bank",
            "issue_url": "https://portal.yivi.app/attribute-index/credentials/demo/VeriD/bankIncomeProfile",
            "should_be_singleton": True,
        },
    )

    attrs = [
        ("rekeninghouder", "Account holder", "Rekeninghouder"),
        ("bankrekening", "Bank account number", "Bankrekening"),
        ("uitgever", "Issuer", "Uitgever"),
        ("datum_uitgifte", "Date of issuance", "Datum uitgifte"),
        (
            "inkomensprofiel_gelijk",
            "Income profile this month equal to last month",
            "Inkomensprofiel deze maand gelijk aan vorige maand",
        ),
    ]

    for tag, name_en, name_nl in attrs:
        CredentialAttribute.objects.get_or_create(
            credential=credential,
            name_en=name_en,
            defaults={
                "credential_attribute_tag": tag,
                "name_nl": name_nl,
                "description_en": name_en,
                "description_nl": name_nl,
                "optional": False,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0032_alter_credentialattribute_unique_together"),
    ]

    operations = [
        migrations.RunPython(add_bank_income_profile, migrations.RunPython.noop),
    ]
