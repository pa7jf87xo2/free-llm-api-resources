"""Validation script for data.py entries.

Checks that all provider entries in data.py are well-formed and contain
required fields before the README is generated or a PR is merged.
"""

import sys
from typing import Any

from data import PROVIDERS, Provider, RateLimit, Model


REQUIRED_PROVIDER_FIELDS = ["name", "url", "free_tier"]
VALID_RATE_LIMIT_PERIODS = ["minute", "hour", "day", "month"]


def validate_url(url: str) -> bool:
    """Basic URL format check."""
    return url.startswith("http://") or url.startswith("https://")


def validate_rate_limit(rate_limit: RateLimit, context: str) -> list[str]:
    """Validate a RateLimit object and return a list of errors."""
    errors = []
    if rate_limit is None:
        return errors

    if rate_limit.requests is not None and rate_limit.requests <= 0:
        errors.append(f"{context}: rate_limit.requests must be a positive integer")

    if rate_limit.tokens is not None and rate_limit.tokens <= 0:
        errors.append(f"{context}: rate_limit.tokens must be a positive integer")

    if rate_limit.period not in VALID_RATE_LIMIT_PERIODS:
        errors.append(
            f"{context}: rate_limit.period '{rate_limit.period}' is not valid. "
            f"Must be one of: {VALID_RATE_LIMIT_PERIODS}"
        )

    return errors


def validate_model(model: Model, context: str) -> list[str]:
    """Validate a Model object and return a list of errors."""
    errors = []

    if not model.name or not model.name.strip():
        errors.append(f"{context}: model name must not be empty")

    if model.rate_limit is not None:
        errors.extend(validate_rate_limit(model.rate_limit, f"{context} > model '{model.name}'"))

    return errors


def validate_provider(provider: Provider) -> list[str]:
    """Validate a single Provider object and return a list of errors."""
    errors = []
    ctx = f"Provider '{provider.name}'"

    if not provider.name or not provider.name.strip():
        errors.append("A provider has an empty or missing name")
        ctx = "Unknown provider"

    if not provider.url or not validate_url(provider.url):
        errors.append(f"{ctx}: invalid or missing URL '{provider.url}'")

    if provider.api_endpoint is not None and not validate_url(provider.api_endpoint):
        errors.append(f"{ctx}: invalid api_endpoint URL '{provider.api_endpoint}'")

    if provider.notes is not None and not isinstance(provider.notes, str):
        errors.append(f"{ctx}: notes must be a string")

    if provider.rate_limit is not None:
        errors.extend(validate_rate_limit(provider.rate_limit, ctx))

    if provider.models:
        for model in provider.models:
            errors.extend(validate_model(model, ctx))

    return errors


def validate_all_providers(providers: list[Provider]) -> list[str]:
    """Validate all providers and return aggregated errors."""
    all_errors = []

    if not providers:
        all_errors.append("PROVIDERS list is empty")
        return all_errors

    seen_names = {}
    for i, provider in enumerate(providers):
        errors = validate_provider(provider)
        all_errors.extend(errors)

        # Check for duplicate provider names
        name_key = provider.name.strip().lower() if provider.name else f"__unnamed_{i}"
        if name_key in seen_names:
            all_errors.append(
                f"Duplicate provider name detected: '{provider.name}' "
                f"(indices {seen_names[name_key]} and {i})"
            )
        else:
            seen_names[name_key] = i

    return all_errors


def main() -> int:
    """Run validation and print results. Returns exit code."""
    print(f"Validating {len(PROVIDERS)} provider(s)...")
    errors = validate_all_providers(PROVIDERS)

    if errors:
        print(f"\n❌ Validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"✅ All {len(PROVIDERS)} provider(s) passed validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
