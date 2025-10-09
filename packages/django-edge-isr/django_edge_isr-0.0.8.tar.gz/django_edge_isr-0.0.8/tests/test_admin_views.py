import json
import pytest
from django.contrib.auth import get_user_model
from edge_isr import graph


@pytest.mark.django_db
def test_admin_status_requires_staff(client):
    r = client.get("/edge-isr/status/?tag=post:1")
    assert r.status_code in (302, 403)


@pytest.mark.django_db
def test_admin_status_returns_data_for_staff(client):
    url = "http://testserver/post/5/"
    graph.bind(url, ["post:5"])

    User = get_user_model()
    User.objects.create_user(username="staff", password="x", is_staff=True)
    client.login(username="staff", password="x")

    r = client.get("/edge-isr/status/?tag=post:5")
    assert r.status_code == 200
    data = json.loads(r.content)
    assert data["tag"] == "post:5"
    assert url in data["urls"]


@pytest.mark.django_db
def test_admin_status_unknown_tag_returns_empty_urls(client):
    User = get_user_model()
    User.objects.create_user(username="staff", password="x", is_staff=True)
    client.login(username="staff", password="x")

    r = client.get("/edge-isr/status/?tag=notfound:9999")
    assert r.status_code == 200
    data = json.loads(r.content)
    assert data["tag"] == "notfound:9999"
    assert data["urls"] == []
