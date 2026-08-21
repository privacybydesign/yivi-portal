# yivi-portal

Onboarding for parties joining Yivi as an Issuer or a Verifier, including the
Trusted Verifier Program for Relying Parties. Django REST backend in
`portal_backend/` + `yivi_portal/`, React SPA in `portal_spa/`, Yivi login as a
reusable Django app in `yivi_auth/`.

## The position it takes

Part of the **Yivi** platform: attribute-based identity, where a person holds
credentials on their own device and discloses only the attributes asked for. Not
part of **Yivi Business Wallet**, which is a separate product in its own repo — a
fix here does not belong there, and the reverse holds too.

The portal is written with an outlook toward EUDI Wallet terminology and maps the
terms explicitly, so **the mapping is the thing to get right**: a Yivi *Issuer* is
an *Attestation Provider* here, a Yivi *Verifier* is a *Relying Party*, and a Yivi
*Scheme* is a *Trust Model Environment*. Code or copy that reaches for a Yivi term
where this project uses the EUDI one reads as correct and is wrong. The full table
is in the README.

One company, two GitHub orgs: `privacybydesign` is the Yivi/IRMA lineage,
`encryption4all` the vehicle the PostGuard research project used to apply for
grants, kept after Yivi bought PostGuard. The split is historical, not
organisational — same company, same maintainers, same review conventions, and we
are maintainers on both sides rather than outside contributors.

## Repos a change here has to consider

- `privacybydesign/pbdf-schememanager`, `pbdf-staging`, `irma-demo-schememanager`
  and `pbdf-requestors` — the scheme repositories the `trusted_aps` and
  `trusted_rps` crons import from, wired in `config.json`. The Attestation
  Providers and Relying Parties in this database originate there; the portal
  presents them and does not own them.
- `privacybydesign/irmago` — the Yivi stack that defines the scheme format those
  importers parse, and the Yivi server `yivi_auth` starts its disclosure sessions
  against.
- `privacybydesign/yivi-frontend-packages` — publishes
  `@privacybydesign/yivi-frontend`, the SPA's disclosure widget.
- `privacybydesign/yivi-businesswallet` — the other product. Do not converge them.

`gabi`, `irmago` and `irmamobile` carry no `CLAUDE.md` by decision. That is the
intended state; do not add one.

## Where the operational knowledge is

Not in this file. Build, test and CI detail that costs real time is in
[`docs/development.md`](docs/development.md). A durable check belongs in the host's
rule bundle, which lands in the next container at `~/dobby-rules.md` — one rule per
check, at most 600 bytes each.

What this file used to be is a list of everything an agent had ever noticed here:
3,704 bytes at `5db8ba8`, the last revision carrying it
(`git show 5db8ba8:CLAUDE.md`). It is not migrated and not reconstructed.
`portal_backend/tests/test_claude_md_orientation.py` holds this file to 4,000
bytes.
