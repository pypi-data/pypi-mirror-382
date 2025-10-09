from edge_isr import graph
from edge_isr.revalidate import tasks as reval


def test_revalidate_purges_and_warmups(monkeypatch):
    url = "http://testserver/post/77/"
    graph.bind(url, ["post:77"])

    purged = []

    class StubCDN:
        def purge_urls(self, urls):
            purged.extend(urls)

    monkeypatch.setattr("edge_isr.revalidate.tasks.get_cdn_connector", lambda: StubCDN())

    class ImmediateQueue:
        def enqueue(self, fn, *args, **kwargs):
            return fn(*args, **kwargs)

    monkeypatch.setattr(
        "edge_isr.revalidate.tasks.get_queue_adapter", lambda *a, **k: ImmediateQueue()
    )

    warmed = []

    def fake_get(u, headers=None, timeout=None):
        warmed.append((u, headers or {}))

        class Resp:
            status_code = 200

        return Resp()

    monkeypatch.setattr("edge_isr.revalidate.tasks.requests.get", fake_get)

    urls = reval.revalidate_by_tags(["post:77"])

    assert url in urls
    assert purged == [url]
    assert warmed and warmed[0][0] == url
    assert warmed[0][1].get("X-Edge-ISR-Warmup") == "1"


# append to file
def test_revalidate_handles_non_200_warmup(monkeypatch):
    url = "http://testserver/post/88/"
    graph.bind(url, ["post:88"])

    purged = []

    class StubCDN:
        def purge_urls(self, urls):
            purged.extend(urls)

    monkeypatch.setattr("edge_isr.revalidate.tasks.get_cdn_connector", lambda: StubCDN())

    class ImmediateQueue:
        def enqueue(self, fn, *args, **kwargs):
            return fn(*args, **kwargs)

    monkeypatch.setattr(
        "edge_isr.revalidate.tasks.get_queue_adapter", lambda *a, **k: ImmediateQueue()
    )

    def fake_get(u, headers=None, timeout=None):
        class Resp:
            status_code = 500

        return Resp()

    monkeypatch.setattr("edge_isr.revalidate.tasks.requests.get", fake_get)

    urls = reval.revalidate_by_tags(["post:88"])
    assert url in urls
    assert purged == [url]
