# django-edge-isr 🚀
[![GitHub stars](https://img.shields.io/github/stars/HamaBarhamou/django-edge-isr?style=social)](https://github.com/HamaBarhamou/django-edge-isr/stargazers)

> If this project is useful to you, please **star the repo** ⭐️.
> Your support helps us prioritize features and keep improving!

**Incremental Static Revalidation for Django** — get **static-like speed** with **dynamic freshness**. Serve fast cached pages at the edge (CDN or proxy) while **revalidating in the background** and rebuilding **only what changed**.

> ⚠️ **Alpha** — APIs may evolve. Feedback & contributions welcome!

<p align="left">
  <a href="https://pypi.org/project/django-edge-isr/"><img alt="PyPI" src="https://img.shields.io/pypi/v/django-edge-isr"></a>
  <a href="https://pypi.org/project/django-edge-isr/"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/django-edge-isr"></a>
  <a href="https://github.com/HamaBarhamou/django-edge-isr/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-green.svg"></a>
  <a href="https://hamabarhamou.github.io/django-edge-isr/"><img alt="Docs" src="https://img.shields.io/badge/docs-latest-blue"></a>
</p>

---

## 📚 Documentation

* **Site (latest)** → [https://hamabarhamou.github.io/django-edge-isr/](https://hamabarhamou.github.io/django-edge-isr/)
* **Quickstart** → [https://hamabarhamou.github.io/django-edge-isr/quickstart/](https://hamabarhamou.github.io/django-edge-isr/quickstart/)
* **Concepts** → [https://hamabarhamou.github.io/django-edge-isr/concepts/](https://hamabarhamou.github.io/django-edge-isr/concepts/)
* **API Reference** → [https://hamabarhamou.github.io/django-edge-isr/api/](https://hamabarhamou.github.io/django-edge-isr/api/)
* **Admin / Status** → [https://hamabarhamou.github.io/django-edge-isr/admin/](https://hamabarhamou.github.io/django-edge-isr/admin/)
* **Revalidation Pipeline** → [https://hamabarhamou.github.io/django-edge-isr/revalidation/](https://hamabarhamou.github.io/django-edge-isr/revalidation/)
* **Deployment** → [https://hamabarhamou.github.io/django-edge-isr/deployment/](https://hamabarhamou.github.io/django-edge-isr/deployment/)
* **Troubleshooting** → [https://hamabarhamou.github.io/django-edge-isr/troubleshooting/](https://hamabarhamou.github.io/django-edge-isr/troubleshooting/)
* **Contributing** → [https://hamabarhamou.github.io/django-edge-isr/contributing/](https://hamabarhamou.github.io/django-edge-isr/contributing/)
* **Release guide** → [https://hamabarhamou.github.io/django-edge-isr/release/](https://hamabarhamou.github.io/django-edge-isr/release/)
* **Changelog** → [https://hamabarhamou.github.io/django-edge-isr/CHANGELOG/](https://hamabarhamou.github.io/django-edge-isr/CHANGELOG/)

---

## 💡 Why

Keeping Django pages **fresh** without over-purging is hard:

* ⏳ **TTL vs correctness** — wait for TTL (stale) or purge everything (origin stampede)
* 🧩 **Ad-hoc invalidation** — brittle, duplicated per view/model
* 🌐 **CDN gap** — Django doesn’t natively speak modern edge semantics like SWR or URL-level purges
* 🧠 **No first-class dependency mapping** — “this page depends on these objects” is missing

**`django-edge-isr`** brings a modern ISR + SWR developer experience **inside Django**, without a static site generator.

---

## ✨ Current status (alpha)

* ✅ `@isr(...)` **for views** (full pages)
* ✅ **SWR headers** via middleware (`public`, `s-maxage`, `stale-while-revalidate`)
* ✅ **Redis tag graph** mapping `url ↔ tags`
* ✅ **Revalidation & warmup** (inline queue by default)
* ✅ **Admin/status endpoints**
* 🧪 **Cloudflare connector** — *experimental*
* 🛠️ **Planned**: CloudFront connector, Celery/RQ adapters, fragment decorator, metrics, improved Admin UX

> No optional install extras (**Celery/RQ/CloudFront**) yet — we’ll announce them once stabilized.

---

## ⚙️ Install

```bash
pip install django-edge-isr
```

**Requirements**: Python 3.10+, Django 4.2/5.x, Redis (for the tag graph & job state)

---

## 🚀 Quickstart

**1) Settings**

```python
# settings.py
INSTALLED_APPS += ["edge_isr"]

MIDDLEWARE += [
    "edge_isr.middleware.EdgeISRMiddleware",  # injects default SWR headers
]

EDGE_ISR = {
    "REDIS_URL": "redis://localhost:6379/0",
    "DEFAULTS": {"s_maxage": 300, "stale_while_revalidate": 3600},

    # Optional (experimental): Cloudflare connector
    # "CDN": {"provider": "cloudflare", "zone_id": "...", "api_token": "..."},

    # Queue: inline for dev; Celery/RQ planned
    # "QUEUE": {"backend": "celery", "queue_name": "edge_isr"},
}
```

**2) Tag your pages**

```python
# urls.py
from edge_isr import isr, tag

@isr(tags=lambda req, post_id: [tag("post", post_id)], s_maxage=300, swr=3600)
def post_detail(request, post_id):
    post = Post.objects.select_related("category").get(pk=post_id)
    request.edge_isr.add_tags([tag("category", post.category_id)])  # add dynamic tags
    return render(request, "post_detail.html", {"post": post})
```

**3) Revalidate on data changes**

```python
# models.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from edge_isr import revalidate_by_tags, tag

@receiver([post_save, post_delete], sender=Post)
def _post_changed(sender, instance, **kw):
    revalidate_by_tags([tag("post", instance.pk), tag("category", instance.category_id)])
```

**Admin / status (optional)**

```python
# urls.py
from django.urls import include, path
urlpatterns = [
    # ...
    path("edge-isr/", include("edge_isr.admin.urls")),
]
```

---

## 🧠 Concepts

* **Tags** — strings like `post:42`, `category:7` declared by views (and fragments later)
* **Tag Graph** — Redis keeps `tag → {urls}` and `url → {tags}`
* **Revalidation** — on changes, resolve URLs by tag, **purge** (optional CDN), then **warm**
* **SWR** — responses include `Cache-Control: public, s-maxage=N, stale-while-revalidate=M` (+ `ETag` when appropriate)

---

## ✅ Compatibility

* **Python**: 3.10+
* **Django**: 4.2, 5.x
* **Redis**: required
* **CDN**: optional (Cloudflare **experimental**), CloudFront **planned**
* **Queues**: inline today; Celery/RQ **planned**

---

## 🚫 When not to use

* Heavily personalized or private pages (varies by user/cookie)
* Non-idempotent endpoints

---

## 🗺️ Roadmap

* **v0.1**: SWR headers, manual tags, Redis tag graph, Cloudflare purge (experimental), warmup, basic Admin
* **v0.2**: CloudFront connector, auto-tagging helpers, **fragment decorator**
* **v0.3**: Admin UX, metrics, locale/device cache keys, smarter warmup (rate-limit, batching)

---

## ❓ FAQ

**Do I need a CDN?**
No. You can start locally or behind Nginx/Varnish. A CDN gives global edge caching and instant purges.

**How do you avoid origin stampede?**
SWR serves a **stale** version while a single background warmup refreshes the cache.

**How do I tag template fragments?**
*Planned for v0.2.* In v0.1 use `@isr` on full views. A possible future API (subject to change):

Python — fragment decorator:

```python
from edge_isr import isr_fragment, tag

@isr_fragment(tags=lambda post: [tag("post", post.id)], s_maxage=300, swr=3600)
def render_post_card(post):
    ...
```

Django template — fragment cache tag:

{% raw %}

```django
{% isrcache "post_card" tags=["post:{{ post.id }}"] %}
  {% include "components/post_card.html" %}
{% endisrcache %}
```

{% endraw %}

---

## 🤝 Contributing

Issues & PRs welcome! See the guide:
[https://hamabarhamou.github.io/django-edge-isr/contributing/](https://hamabarhamou.github.io/django-edge-isr/contributing/)

* **Release guide**: [https://hamabarhamou.github.io/django-edge-isr/release/](https://hamabarhamou.github.io/django-edge-isr/release/)
* **Changelog**: [https://hamabarhamou.github.io/django-edge-isr/CHANGELOG/](https://hamabarhamou.github.io/django-edge-isr/CHANGELOG/)

---

## 📄 License

[MIT](LICENSE)
