from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from ..graph import urls_for, tags_for


@staff_member_required
def status(request):
    tag = request.GET.get("tag")
    url = request.GET.get("url")
    if tag:
        return JsonResponse({"tag": tag, "urls": urls_for([tag])})
    if url:
        return JsonResponse({"url": url, "tags": tags_for(url)})
    return JsonResponse({"ok": True})
