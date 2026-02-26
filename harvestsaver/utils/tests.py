from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_post(request):
    return JsonResponse({"ok": True})