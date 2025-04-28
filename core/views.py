# core/views.py
from django.http import JsonResponse
from core.models import ApplicationVersion


def version_info(request):
    try:
        current_version = ApplicationVersion.objects.latest('release_date')
    except ApplicationVersion.DoesNotExist:
        return JsonResponse({'error': 'No version information available.'}, status=404)

    return JsonResponse({'version': current_version.version})