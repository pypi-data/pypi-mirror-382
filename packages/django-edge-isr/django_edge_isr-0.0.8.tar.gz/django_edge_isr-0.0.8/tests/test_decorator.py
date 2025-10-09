from edge_isr.graph import tags_for


def test_decorator_overrides_headers_and_binds(client):
    resp = client.get("/post/123/")
    cc = resp.headers.get("Cache-Control", "")
    assert "s-maxage=30" in cc
    assert "stale-while-revalidate=300" in cc
    assert "post:123" in tags_for("http://testserver/post/123/")


def test_vary_option_sets_header(client):
    resp = client.get("/vary/")
    assert "Accept-Language" in (resp.headers.get("Vary", "") or "")


def test_vary_is_merged(client):
    resp = client.get("/vary-merge/")
    v = resp.headers.get("Vary", "")
    assert "Accept-Language" in v
    assert "User-Agent" in v


def test_no_bind_on_non_200(client):
    from edge_isr.graph import urls_for

    resp = client.get("/non200/")
    assert resp.status_code == 404
    assert urls_for(["non200:test"]) == []


# append to file
def test_no_tags_does_not_bind(client):
    from edge_isr.graph import tags_for

    url = "http://testserver/no-tags/"
    resp = client.get("/no-tags/")
    assert resp.status_code == 200
    assert list(tags_for(url)) == []


def test_vary_dedup_merge_multiple(client):
    resp = client.get("/vary-dedupe/")
    v = resp.headers.get("Vary", "")
    assert "User-Agent" in v
    assert "Accept-Language" in v
    assert "Accept-Encoding" in v
    # ensure no duplicates for Accept-Language
    assert v.count("Accept-Language") == 1
