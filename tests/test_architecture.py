from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import src

PACKAGE_ROOT = src


@pytest.mark.architecture
def test_domain_layer_is_isolated(archrule):
    """Domain models must not depend on application, infrastructure, or entrypoints."""

    (
        archrule("domain-is-isolated", "Domain layer stays pure")
        .match("src.domain", "src.domain.*")
        .should_not_import(
            "src.application",
            "src.application.*",
            "src.infra",
            "src.infra.*",
            "src.entrypoints",
            "src.entrypoints.*",
        )
        .check(PACKAGE_ROOT)
    )


@pytest.mark.architecture
def test_application_layer_is_between_domain_and_infra(archrule):
    """Application layer may depend on domain but not on infra/entrypoints."""

    (
        archrule("application-keeps-boundaries", "Application layer stays above infra")
        .match("src.application", "src.application.*")
        .should_not_import(
            "src.infra",
            "src.infra.*",
            "src.entrypoints",
            "src.entrypoints.*",
        )
        .check(PACKAGE_ROOT)
    )


@pytest.mark.architecture
def test_infra_does_not_depend_on_entrypoints(archrule):
    """Infrastructure code should never import entrypoints."""

    (
        archrule("infra-keeps-out-entrypoints", "Infra stays below entrypoints")
        .match("src.infra", "src.infra.*")
        .should_not_import("src.entrypoints", "src.entrypoints.*")
        .check(PACKAGE_ROOT)
    )
