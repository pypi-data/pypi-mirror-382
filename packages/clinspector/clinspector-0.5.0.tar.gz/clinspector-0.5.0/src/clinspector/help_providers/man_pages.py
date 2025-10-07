"""Man page provider implementation using man-api.ch."""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass
from pathlib import Path
import re
from typing import TYPE_CHECKING

import hishel
import httpx

from clinspector.help_providers.base import CommandHelp, HelpProvider


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from clinspector.help_providers.base import Example


@dataclass
class ManSection:
    """Man page section info."""

    number: str
    """Section number (1-9)."""
    name: str
    """Name of the command/topic."""


@contextlib.asynccontextmanager
async def get_client() -> AsyncIterator[httpx.AsyncClient]:
    """Get a configured httpx client with caching."""
    cache_dir = Path("~/.cache/clinspector/man_pages").expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)

    storage = hishel.AsyncFileStorage(
        base_path=Path(cache_dir),
        ttl=60 * 60 * 24,  # 24 hours
    )

    controller = hishel.Controller(
        cacheable_methods=["GET"],
        cacheable_status_codes=[200],
        allow_stale=True,
    )

    transport = hishel.AsyncCacheTransport(
        transport=httpx.AsyncHTTPTransport(),
        storage=storage,
        controller=controller,
    )

    async with httpx.AsyncClient(
        transport=transport,
        headers={
            "User-Agent": "clinspector/0.1.0",
            "Accept": "text/plain",
        },
        timeout=10.0,
    ) as client:
        yield client


class ManPageProvider(HelpProvider):
    """Provider for man pages via man-api.ch."""

    BASE_URL = "https://man-api.ch/v1/buster"

    def _parse_man_ref(self, ref: str) -> ManSection:
        """Parse a man page reference like 'git(1)' into section and name.

        Defaults to section 1 (user commands) if not specified.
        """
        if match := re.match(r"([^(]+)\((\d+)\)", ref):
            return ManSection(number=match.group(2), name=match.group(1).lower())
        # No section specified - default to section 1
        return ManSection(number="1", name=ref.lower())

    def _parse_page(self, content: str) -> CommandHelp:
        """Parse man page content into CommandHelp structure."""
        lines = content.splitlines()
        name = ""
        description = ""
        examples: list[Example] = []
        current_section = ""

        # Temporary collectors
        description_lines: list[str] = []
        current_paragraph: list[str] = []

        def flush_paragraph():
            """Join collected lines into a clean paragraph."""
            if current_paragraph:
                text = " ".join(current_paragraph).strip()
                # Clean up common formatting artifacts
                text = re.sub(r"\s+", " ", text)
                text = text.replace("- ", "")
                if current_section == "DESCRIPTION":
                    description_lines.append(text)
                current_paragraph.clear()

        line_iter = iter(lines)
        for line in line_iter:
            line = line.rstrip()

            # Section headers are usually uppercase
            if line and line.upper() == line and not line.startswith(" "):
                flush_paragraph()
                current_section = line.strip()
                continue

            # Handle NAME section specially
            if current_section == "NAME":
                if " - " in line:
                    name, desc = line.split(" - ", 1)
                    name = name.strip()
                    description_lines.append(desc.strip())
                continue

            # Collect DESCRIPTION content
            if current_section == "DESCRIPTION":
                # New paragraph on empty line
                if not line.strip():
                    flush_paragraph()
                else:
                    # Add to current paragraph, handling line wrapping
                    current_paragraph.append(line.strip())

        # Flush any remaining paragraph
        flush_paragraph()

        # Join description paragraphs with newlines
        description = "\n\n".join(description_lines)

        return CommandHelp(
            name=name, description=description, examples=examples, platform="linux"
        )

    async def get_command_help(self, command: str) -> CommandHelp:
        """Get man page for a command."""
        section = self._parse_man_ref(command)
        url = f"{self.BASE_URL}/{section.number}/{section.name}"

        async with get_client() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return self._parse_page(response.text)
            except httpx.HTTPStatusError as exc:
                msg = (
                    f"Failed to fetch man page for {command}: {exc.response.status_code}"
                )
                raise ValueError(msg) from exc
            except httpx.TimeoutException as exc:
                msg = f"Timeout fetching man page for {command}"
                raise ValueError(msg) from exc

    async def search_commands(self, query: str) -> list[str]:
        """Search is not supported by the API."""
        msg = "Man page API does not support searching"
        raise NotImplementedError(msg)

    async def list_commands(self) -> list[str]:
        """Listing is not supported by the API."""
        msg = "Man page API does not support listing all commands"
        raise NotImplementedError(msg)


if __name__ == "__main__":

    async def main():
        provider = ManPageProvider()
        print(await provider.list_commands())

    asyncio.run(main())
