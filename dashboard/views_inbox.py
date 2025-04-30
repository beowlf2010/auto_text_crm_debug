# dashboard/views_inbox.py
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET

from dashboard.models import MessageLog


@require_GET
def get_message_history(request, lead_id: int):
    """
    JSON list of all MessageLog rows for the given lead, ordered oldest → newest.

    Example response element:
    {
        "id": 17,
        "content": "Hello!",
        "source": "Manual",
        "direction": "OUT",
        "timestamp": "2025-04-17 16:42",
        "read": false
    }
    """
    # quick existence check to return 404 on bad ID
    if not MessageLog.objects.filter(lead_id=lead_id).exists():
        raise Http404("Lead not found")

    messages = (
        MessageLog.objects.filter(lead_id=lead_id)
        .order_by("timestamp")
        .values(
            "id",
            "content",
            "source",
            "direction",
            "timestamp",
            "read",
        )
    )

    # format timestamp as string to keep the old contract
    data = [
        {
            **m,
            "timestamp": m["timestamp"].strftime("%Y-%m-%d %H:%M"),
        }
        for m in messages
    ]
    return JsonResponse(data, safe=False)
