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
