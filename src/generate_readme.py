#!/usr/bin/env python3
"""Script to generate README.md from template and data.

This script reads the data from data.py and the README template,
then generates the final README.md with up-to-date provider information.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure src directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from data import (
    PROVIDERS,
    Provider,
    ModelTier,
)


REPO_ROOT = Path(__file__).parent.parent
TEMPLATE_PATH = Path(__file__).parent / "README_template.md"
OUTPUT_PATH = REPO_ROOT / "README.md"


def format_rate_limit(provider: Provider) -> str:
    """Format rate limit information for a provider."""
    limits = []
    if provider.requests_per_minute:
        limits.append(f"{provider.requests_per_minute} req/min")
    if provider.requests_per_day:
        limits.append(f"{provider.requests_per_day} req/day")
    if provider.tokens_per_minute:
        limits.append(f"{provider.tokens_per_minute:,} tokens/min")
    if provider.tokens_per_day:
        limits.append(f"{provider.tokens_per_day:,} tokens/day")
    return ", ".join(limits) if limits else "Unknown"


def format_models(provider: Provider) -> str:
    """Format model list for a provider, grouping by tier."""
    if not provider.models:
        return "Various"

    free_models = [m for m in provider.models if m.tier == ModelTier.FREE]
    if not free_models:
        free_models = provider.models

    model_names = [m.name for m in free_models]
    if len(model_names) > 5:
        return ", ".join(model_names[:5]) + f" (+{len(model_names) - 5} more)"
    return ", ".join(model_names)


def build_provider_table(providers: list[Provider]) -> str:
    """Build a markdown table of providers."""
    headers = ["Provider", "Free Models", "Rate Limits", "Requires CC", "Notes"]
    separator = ["---"] * len(headers)

    rows = [headers, separator]

    for provider in sorted(providers, key=lambda p: p.name.lower()):
        name_cell = f"[{provider.name}]({provider.url})"
        models_cell = format_models(provider)
        rate_limit_cell = format_rate_limit(provider)
        requires_cc = "Yes" if provider.requires_credit_card else "No"
        notes = provider.notes or ""

        rows.append([name_cell, models_cell, rate_limit_cell, requires_cc, notes])

    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def generate_readme() -> str:
    """Generate the full README content from template and data."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Build provider table
    active_providers = [p for p in PROVIDERS if not getattr(p, "deprecated", False)]
    provider_table = build_provider_table(active_providers)

    # Format update timestamp
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    # Replace template placeholders
    content = template.replace("{{PROVIDER_TABLE}}", provider_table)
    content = content.replace("{{PROVIDER_COUNT}}", str(len(active_providers)))
    content = content.replace("{{LAST_UPDATED}}", timestamp)

    return content


def main() -> int:
    """Main entry point for README generation."""
    try:
        print(f"Reading template from: {TEMPLATE_PATH}")
        readme_content = generate_readme()

        print(f"Writing README to: {OUTPUT_PATH}")
        OUTPUT_PATH.write_text(readme_content, encoding="utf-8")

        print(f"Successfully generated README.md with {len(PROVIDERS)} providers.")
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
