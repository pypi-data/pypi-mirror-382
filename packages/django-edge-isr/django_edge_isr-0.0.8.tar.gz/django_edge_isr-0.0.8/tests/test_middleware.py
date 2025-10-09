def test_middleware_sets_default_swr_headers(client):
    resp = client.get("/basic/")
    cc = resp.headers.get("Cache-Control", "")
    assert "public" in cc
    assert "s-maxage=60" in cc
    assert "stale-while-revalidate=600" in cc
