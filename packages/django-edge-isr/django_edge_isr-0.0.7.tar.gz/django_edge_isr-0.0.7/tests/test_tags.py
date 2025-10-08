from edge_isr import tag


def test_tag_format():
    assert tag("post", 42) == "post:42"
    assert tag("category", "7") == "category:7"
