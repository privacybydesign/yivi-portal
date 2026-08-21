import re
from pathlib import Path

from django.test import SimpleTestCase

REPO_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

MAX_BYTES = 4000

# The headings the operational corpus filled the file under until it was cut. The
# byte cap alone would let it grow back one bullet at a time, so the sections are
# named too.
CUT_SECTIONS = ("portal_spa", "portal_backend", "CI")


class ClaudeMdOrientationTest(SimpleTestCase):
    """CLAUDE.md is orientation: what this repo is, where it sits, and which repos a
    change here touches. Detail belongs in docs/development.md or in the rule bundle."""

    def test_stays_under_the_size_cap(self):
        """4,000 B is the gate that decides whether a container working this repo gets
        its cwd pointed at the clone, so growing past it costs more than tidiness."""
        size = CLAUDE_MD.stat().st_size
        self.assertLessEqual(
            size,
            MAX_BYTES,
            f"CLAUDE.md is {size} B, over the {MAX_BYTES} B cap. Build and test detail "
            "goes in docs/development.md; a durable check goes in the rule bundle.",
        )

    def test_has_no_heading_from_the_cut_corpus(self):
        """A returning section is the same regression starting over."""
        headings = [
            line.lstrip("#").strip()
            for line in CLAUDE_MD.read_text(encoding="utf-8").splitlines()
            if line.startswith("#")
        ]
        for heading in headings:
            # Whole tokens, not the whole heading: a section comes back under a
            # longer name ("Frontend (`portal_spa`)") as readily as under its old
            # one, and equality waves that through. `\w` keeps `portal_spa` a single
            # token while splitting "yivi-portal", this file's own title.
            tokens = {token.casefold() for token in re.findall(r"\w+", heading)}
            for section in CUT_SECTIONS:
                self.assertNotIn(
                    section.casefold(),
                    tokens,
                    f'CLAUDE.md heading "{heading}" names "{section}" again. That '
                    "section was cut with the operational corpus; its content lives "
                    "in docs/development.md now.",
                )
