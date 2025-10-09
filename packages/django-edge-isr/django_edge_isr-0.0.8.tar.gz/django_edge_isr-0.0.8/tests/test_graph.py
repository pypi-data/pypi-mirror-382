from edge_isr import tag
from edge_isr import graph


def test_bind_and_urls_for():
    url = "http://testserver/post/1/"
    t = tag("post", 1)
    graph.bind(url, [t])
    assert url in graph.urls_for([t])


def test_unbind_removes_both_sides():
    url = "http://testserver/post/2/"
    t = tag("post", 2)
    graph.bind(url, [t])
    graph.unbind(url)
    assert url not in graph.urls_for([t])


def test_urls_for_union_across_multiple_tags():
    a, b = "t:a", "t:b"
    u1 = "http://testserver/a/1/"
    u2 = "http://testserver/b/2/"
    u3 = "http://testserver/ab/3/"
    graph.bind(u1, [a])
    graph.bind(u2, [b])
    graph.bind(u3, [a, b])

    urls = set(graph.urls_for([a, b]))
    assert {u1, u2, u3}.issubset(urls)


def test_rebind_adds_tags_without_dup():
    u = "http://testserver/rebind/1/"
    a, b = "t:a", "t:b"
    graph.bind(u, [a])
    graph.bind(u, [a, b])

    from edge_isr.graph import tags_for

    assert set(tags_for(u)) >= {a, b}
    assert u in graph.urls_for([b])
