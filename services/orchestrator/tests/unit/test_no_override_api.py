"""Negative: no Confirmed override API/flag for ignore policy (EP-005 T012 / OQ-OVERRIDE).

Defaults remain enforced; any future override UX stays Proposed only.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.security import ignore_policy as ignore_mod


def test_openapi_has_no_override_ignore_endpoint() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    paths = schema.get("paths") or {}
    # No Confirmed override / force-include surface
    for path in paths:
        lower = path.lower()
        assert "override" not in lower
        assert "force-include" not in lower
        assert "allow-secret" not in lower

    # Index request schema must not advertise override flags
    components = (schema.get("components") or {}).get("schemas") or {}
    index_req = components.get("IndexRequest") or {}
    props = set((index_req.get("properties") or {}).keys())
    forbidden = {
        "override",
        "force_include",
        "include_excluded",
        "allow_secrets",
        "bypass_ignore",
    }
    assert props.isdisjoint(forbidden), f"IndexRequest leaked override props: {props & forbidden}"


def test_ignore_module_documents_oq_override_open() -> None:
    doc = ignore_mod.__doc__ or ""
    assert "OQ-OVERRIDE" in doc
    assert not hasattr(ignore_mod.IgnorePolicy, "override")
    assert not hasattr(ignore_mod.IgnorePolicy, "force_include")
