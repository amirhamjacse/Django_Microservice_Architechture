import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health(_request):
    services = {
        "gateway": {"status": "ok"},
        "user-service": _check_service(f"{settings.USER_SERVICE_URL}/health/"),
        "post-service": _check_service(f"{settings.POST_SERVICE_URL}/health/"),
        "comment-service": _check_service(f"{settings.COMMENT_SERVICE_URL}/health/"),
    }
    overall = "ok" if all(v.get("status") == "ok" for v in services.values()) else "degraded"
    return Response({"service": "api-gateway", "status": overall, "services": services})


@api_view(["GET"])
def feed(_request):
    posts_payload = _safe_get_json(f"{settings.POST_SERVICE_URL}/api/posts/")
    comments_payload = _safe_get_json(f"{settings.COMMENT_SERVICE_URL}/api/comments/")

    posts = _extract_results(posts_payload)
    comments = _extract_results(comments_payload)

    comments_by_post = {}
    for comment in comments:
        post_id = comment.get("post_id")
        comments_by_post.setdefault(post_id, []).append(comment)

    merged = []
    for post in posts:
        merged.append(
            {
                "post": post,
                "comments": comments_by_post.get(post.get("id"), []),
            }
        )

    return Response({"count": len(merged), "data": merged})


def _check_service(url):
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return {"status": "ok"}
        return {"status": "error", "code": response.status_code}
    except requests.RequestException:
        return {"status": "down"}


def _safe_get_json(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        return []
    return []


def _extract_results(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list):
            return results
    return []
