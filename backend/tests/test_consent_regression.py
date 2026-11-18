"""Focused FastAPI regression: synthetic-only partner consent protections."""
import os
import tempfile
# Imported test suite sets CARRIER_DB and creates isolated TestClient in CI.
from test_api import cl, mk, res, cons, view


def test_one_sided_consent_and_revoke_immediately_block_both_partners():
    cid, a, b = mk()
    res(cid, a, HBB="1")
    res(cid, b, HBB="1")
    cons(cid, a, True)
    for actor in (a, b):
        v = view(cid, actor)
        assert v["genes_shown"] == []
        assert "25%" not in str(v)
    cons(cid, b, True)
    for actor in (a, b):
        assert view(cid, actor)["genes_shown"] == ["HBB"]
    cons(cid, b, False)
    for actor in (a, b):
        v = view(cid, actor)
        assert v["genes_shown"] == []
        assert "25%" not in str(v)
